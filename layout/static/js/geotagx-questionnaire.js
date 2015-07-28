/*
 * The GeoTag-X questionnaire helper.
 */
;(function(geotagx, $, undefined){
	"use strict";

	var api_ = {}; // The questionnaire API.
	var answers_ = {}; // The questionnaire's answers.
	var $questions_ = null; // The set of questions.
    var numberOfQuestions_ = 0; // The number of questions asked in this project, including the spam filter.
	var initialQuestion_ = 0; // The questionnaire's initial question.
    var percentageComplete_ = 0; // The percentage of questions completed.
    var progress_ = []; // A stack used to track the user's progress throughout the questionnaire. It also allows a user to rewind to a previous question.
	var olMap_ = null; // The OpenLayers 3 map instance.

	$(document).ready(function(){
		$questions_ = $(".question");
		numberOfQuestions_ = $questions_.length;
		initialQuestion_ = $questions_.first().data("id");

		$("#questionnaire-rewind").on("click", showPreviousQuestion);

		// Set the 'Show Comments' button handlers. One event handler loads the Disqus thread once and is disabled.
		// The next handler simply makes the #disqus_thread div visible.
		$("#questionnaire-show-comments").on("click.loadDisqus", function(){
			var disqus_shortname = 'geotagx'; (function(){var dsq = document.createElement('script'); dsq.type = 'text/javascript'; dsq.async = true; dsq.src = '//' + disqus_shortname + '.disqus.com/embed.js';(document.getElementsByTagName('head')[0] || document.getElementsByTagName('body')[0]).appendChild(dsq);})();
			$(this).off("click.loadDisqus");
		}).click(function(){
			$(this).fadeOut(100, function(){
				$(this).addClass("hide");
				$("#questionnaire-hide-comments").removeClass("hide").hide().fadeIn();
				$("#disqus_thread").removeClass("hide").hide().fadeIn(100);
			});
		});

		// Set the 'Hide Comments' button handler.
		$("#questionnaire-hide-comments").click(function(){
			$(this).fadeOut(100, function(){
				$(this).addClass("hide");
				$("#questionnaire-show-comments").removeClass("hide").hide().fadeIn();
				$("#disqus_thread").fadeOut(100, function(){ $(this).addClass("hide"); });
			});
		});

		// Set help modal trigger handlers.
		$(".help-toggle").click(function(){
			var siblings = $(this).siblings("div.modal");
			if (siblings.length > 0)
				$(siblings[0]).modal(); // The first (and most likely only) sibling should be a modal div; toggle its visibility.
		});

		// Set answer button handlers.
		$(".btn-answer").on("click.questionnaire", function(){
			var $submitter = $(this);
			var question = api_.getCurrentQuestion();
			var answer = parseAnswer(api_.getQuestionType(question), $submitter);

			// Save the answer.
			var storageKey = getStorageKey(question);
			if (storageKey)
				saveAnswer(storageKey, answer);

			showNextQuestion(question, answer, $submitter);
		});

		// Initialize the answers_ object's properties. A property is located in each
		// element with the 'answer' class, that has a non-empty 'key' data attribute.
		$(".answer").each(function(){
			var property = $.trim($(this).data("key"));
			if (property)
				answers_[property] = null;
		});

		// Create an OpenLayers map iff the container for it exists.
		if (!$.isEmptyObject($("#ol-map"))){
			olMap_ = createOpenLayersMap();

			// Initialize the map's search function.
			var $olMapSearchInput = $("#ol-map-search-input");
			var $olMapSearchButton = $("#ol-map-search-button");

			$olMapSearchInput.on("keypress", function(e){
				var keycode = (e.keyCode ? e.keyCode : e.which);
				if (keycode === 13 && $.trim($olMapSearchInput.val())){ // Code 13 corresponds to the 'Enter' key.
					e.preventDefault();
					$olMapSearchButton.trigger("click");
				}
			}).on("input", function(){ //TODO Throttle/debounce this.
				// Disable the search button if there's no user input, enable it otherwise.
				$olMapSearchButton.prop("disabled", !$(this).val());
			});

			$olMapSearchButton.on("click", function(){
				var location = $.trim($olMapSearchInput.val());
				if (location){
					$.getJSON("http://nominatim.openstreetmap.org/search/" + location + "?format=json&limit=1", function(results){
						if (results.length > 0){
							var result = results[0];

							// Replace the search string with the result's display name, i.e. the city name, then center the map.
							$olMapSearchInput.val(result.display_name);

							var view = olMap_.getView();
							view.setCenter(ol.proj.transform([parseFloat(result.lon), parseFloat(result.lat)], "EPSG:4326", "EPSG:3857"));
							view.setZoom(7);
	                    }
	                    else
	                        console.log("Location not found!"); // e.g. xyxyxyxyxyxyx
					});
	            }
	        });
		}
		// Set image zoom button handler.
		function zoom(image, delta){
			// Create a wheel event with a pre-calculated point of interest
			// for the zoom algorithm.
			var e = new WheelEvent("wheel", {deltaY:delta});
			e.zoomAt = {
				x:image.width / 2,
				y:image.height / 2
			};

			// Fire the event which should be picked up by the wheelzoom library.
			if (document.dispatchEvent)
				image.dispatchEvent(e);
			else
				image.fireEvent("onwheel", e);
		}
		$("#image-zoom-in").click(function(){ zoom($("#image")[0], -1); });
		$("#image-zoom-out").click(function(){ zoom($("#image")[0], 1); });

		// Initialize datetime pickers.
		$(".datetime-picker").datetimepicker({
			format:"YYYY/MM/DD HH:mm",
			inline:true,
			sideBySide:true,
			icons:{
				"up":"fa fa-2x fa-chevron-up",
				"down":"fa fa-2x fa-chevron-down",
				"next":"fa fa-chevron-right",
				"previous":"fa fa-chevron-left"
			}
		});
	});
	/**
	 * Creates an OpenLayers map.
	 */
	function createOpenLayersMap(){
	    var source = new ol.source.Vector();
		var vector = new ol.layer.Vector({
			source:source,
			style: new ol.style.Style({
				fill:new ol.style.Fill({
					color:"rgba(255, 255, 255, 0.2)"
				}),
				stroke:new ol.style.Stroke({
					color:"#ffcc33",
					width:2
				}),
				image:new ol.style.Circle({
					radius:7,
					fill:new ol.style.Fill({
						color:"#ffcc33"
					})
				})
			})
		});
	    var map = new ol.Map({
			target:"ol-map",
	    	layers:[
				new ol.layer.Tile({source:new ol.source.MapQuest({layer:"osm"})}),
				vector
			],
			view:new ol.View({
				center:[0, 0],
				zoom:1
			})
	    });
		var interaction = new ol.interaction.Draw({source:source, type:"Polygon"});
		interaction.on("drawstart", function(){
			// If a new polygon is being drawn and a previous one exists, delete the old one.
			resetMap(false);
		});
		map.addInteraction(interaction);

		return map;
	}
	/**
	 * Returns the user's map selection.
	 */
	function getMapSelection(){
		var selection = null;
		if (olMap_){
			// If a polygon (feature) has been drawn, return its vertices in the form of an array of <X, Y> pairs.
			var features = olMap_.getLayers().item(1).getSource().getFeatures();
			if (features.length > 0){
				selection = [];
				var vertices = features[0].getGeometry().getCoordinates()[0];
				$(vertices).each(function(){ selection.push(this); });
			}
		}
		return selection;
	}
	/**
	 * Removes the plotted polygon from the map, and if center is set to true, the map is centered at the origin.
	 */
	function resetMap(center){
		if (olMap_){
			// Remove all features from the vector layer.
			olMap_.getLayers().item(1).getSource().clear();

			// Center the map at the origin and reset the zoom level.
			if (center){
				var view = olMap_.getView();
				view.setCenter([0, 0]);
				view.setZoom(1);
			}
		}
	}
	/**
	 * Returns the identifier of the next question to display. This function
	 * can be overwritten by a user-defined implementation via the
	 * onGetNextQuestion API call.
	 * @param question the current question identifier.
	 */
	function getNextQuestion(question){
		return question + 1;
	}
	/**
	 * A function that determines the next question based on the current question
	 * and its answer. This function can be overwritten by a user-defined
	 * implementation via the onShowNextQuestion API call.
	 * @param question the current question identifier.
	 * @param answer the current question's answer.
	 * @param $submitter the HTML element that submitted the answer to the specified question.
	 */
	function showNextQuestion(question, answer, $submitter){
		api_.showQuestion(getNextQuestion(question, answer, $submitter));
	}
	/**
	 * Displays the previous question, iff it exists.
	 */
	function showPreviousQuestion(){
		// We can only rewind if we've completed at least two questions.
        if (progress_.length >= 2){
            var current  = progress_[progress_.length - 1];
            var previous = progress_[progress_.length - 2];

            // Destroy the current result before loading the previous question.
            saveAnswer(getStorageKey(current), null);

            // Update the progress stack and status panel.
            progress_.pop();
            updateStatus();

            // Disable the rewind button if there're no more previous questions.
            if (progress_.length === 1)
                $("#questionnaire-rewind").prop("disabled", true);

            // Hide the current question and show the previous.
            getQuestionElement(previous).removeClass("hide");
			getQuestionElement(current).addClass("hide");

			// Update analytics parameters.
			geotagx.analytics.onQuestionChanged(previous);
        }
        else
            console.log("[geotagx::questionnaire::showPrevQuestion] Error! Could not load the previous question!");
	};
	/**
	 * Returns the answer submitted by the specified submitter.
	 */
	function parseAnswer(questionType, $submitter){
		/**
		 * Returns the value of an item.
		 */
		function getItemValue($item){
			var output = "";
			if ($item && $item.length > 0){
				// Does the item contain its value in a text input field? If it
				// does, then get the actual value from the text input field.
				var otherInputId = $.trim($item.data("other-input-id"));
				if (otherInputId.length > 0){
					var $otherInput = $("#" + otherInputId);
					if ($otherInput.length > 0){
						var value = $.trim($otherInput.val());
						output = value.length > 0 ? value : "Other";
					}
				}
				else
					output = $.trim($item.val());
			}
			return output;
		}
		/**
		 * Converts a list of item values into a string.
		 */
		function itemValuesToString($items){
			var output = "";
			$items.each(function(){
				var value = getItemValue($(this));
				if (value.length > 0)
					output += ", " + value;
			});
			return output.substring(2); // Remove the leading comma and space.
		}

		var answer = $submitter.attr("value");
		if (answer === "Done"){
			switch (questionType){
				case "dropdown-list":
					// Find the selected item that isn't disabled. Remember that
					// the prompt is selected by default, but disabled to prevent
					// users from ever selecting it.
					var $input = $("#" + $submitter.data("input-id"));
					var $item = $(":checked:not(:disabled)", $input);
					return $item.length > 0 ? $.trim($item.val()) : "None";
				case "select":
					var $item = $("input:checked", $submitter.siblings("label"));
					var value = getItemValue($item);
					return value.length > 0 ? value : "None";
				case "checklist":
					var $checkedItems = $("input:checked", $submitter.siblings("label"));
					var value = itemValuesToString($checkedItems);
					return value.length > 0 ? value : "None";
				case "illustrative-checklist":
					var $illustrations = $(".illustration", $submitter.parent().siblings(".illustrations"));
					var $input = $("input[type='checkbox']:checked", $illustrations);

					answer = $.trim($("input[type='text']", $illustrations).val()); // The user's unlisted answer.
					return answer
					     ? ($input.length === 0 ? answer : answer + ", " + itemValuesToString($input))
					     : ($input.length === 0 ? "None" : itemValuesToString($input));
				case "geotagging":
					return getMapSelection();
				case "url":
				case "text":
				case "longtext":
					return $.trim($("#" + $submitter.data("input-id")).val());
				case "number":
					var numberString = $.trim($("#" + $submitter.data("input-id")).val());
					return numberString ? parseFloat(numberString) : null;
				case "datetime":
					var date = $("#" + $submitter.data("input-id")).data("DateTimePicker").date();
					return date != null
						 ? date.format("X") // Return date and time as a Unix timestamp.
						 : null;
				default:
					console.log("[geotagx::questionnaire::parseAnswer] Error! Unknown question type '" + questionType + "'.");
					return null;
			}
		}
		else
			return answer;
	}
	/**
	 * Saves the specified answer.
	 * @param storageKey the name of the key used to store the answer.
	 * @param answer the answer to save.
	 */
	function saveAnswer(storageKey, answer){
		if (storageKey)
			answers_[storageKey] = $.type(answer) === "undefined" ? null : answer;
	};
	/**
	 * Returns the specified question's HTML node.
	 */
	function getQuestionElement(question){
		return $(".question[data-id='" + question + "']");
	}
	/**
	 * Returns the current question's HTML node.
	 */
	function getCurrentQuestionElement(){
		return getQuestionElement(api_.getCurrentQuestion());
	}
	/**
	 * Updates the questionnaire status, which includes information such
	 * as the user's progress.
	 */
	function updateStatus(){
		// Having sequential question identifiers implies that the user has
		// completed (Q - 1) questions where Q is the current question identifier.
		percentageComplete_ = progress_.length > 0
		                    ? Math.max(0, Math.min(100, (((api_.getCurrentQuestion() - 1) / numberOfQuestions_) * 100).toFixed(0)))
							: 0;

		$("#current-analysis-progress").html(percentageComplete_);
		$("#questionnaire-progress-bar").css("width", percentageComplete_ + "%");

		var $panel = $("#questionnaire-status-panel");
		if (percentageComplete_ == 100)
			$panel.addClass("analysis-complete");
		else
			$panel.removeClass("analysis-complete");
	};
	/**
	 * Resets all user input.
	 */
	function resetInput(){
		$("textarea").val("");
		$("input").removeAttr("checked");
		$("input[type='text']").val("");
		$("input[type='url']").val("");
		$("input[type='number']").val("");
		$(".datetime-picker").data("DateTimePicker").date(null);

		resetMap(true);
	}
	/**
	 * Returns the storage key for the specified question, or null if it doesn't exist.
	 * A storage key is stored in the question's answer div as the "key" data attribute.
	 */
	function getStorageKey(question){
		var storageKey = null;
		var $node = $("div.answer", getQuestionElement(question));
		if ($node){
			var key = $node.data("key");
			if (key)
				storageKey = key;
		}
		return storageKey;
	}
	/**
	 * Starts the questionnaire from the specified question.
	 * If an initial question is not specified, then it is determined automatically.
	 */
	api_.start = function(question){
		$questions_.addClass("hide");

		resetInput();
		progress_ = [];

		// Enable "Show Comments" toggle.
		$("#questionnaire-show-comments").prop("disabled", false);

		// Reset the current task run.
		for (var property in answers_)
			answers_[property] = null;

		// Toggle wheelzoom on the image.
		wheelzoom($("#image"));

		// Override the initial question identifier, if need be.
		if (question && $.type(question) === "number")
			initialQuestion_ = question;

		api_.showQuestion(initialQuestion_);

		// Start a questionnaire tour, if one hasn't already been completed.
		if (!geotagx.tour.questionnaireTourEnded())
			setTimeout(geotagx.tour.startQuestionnaireTour, 1000);
	};
	/**
	 * Returns the number of questions.
	 */
	api_.getNumberOfQuestions = function(){
		return numberOfQuestions_;
	};
	/**
	 * Returns the type of the specified question.
	 */
	api_.getQuestionType = function(question){
		return getQuestionElement(question).data("type");
	};
	/**
	 * Returns the current answer for the specified question.
	 */
	api_.getAnswer = function(question){
		var answer = null;
		var key = getStorageKey(question);
		if (key)
			answer = answers_[key];
		else
			console.log("[geotagx::questionnaire::getAnswer] Warning! Could not find a storage key for question #" + question + ".");

		return answer;
	};
	/**
	 * Returns the current set of answers.
	 */
	api_.getAnswers = function(){
		return answers_;
	};
	/**
	 * Set a user-defined function that is called each time an answer is submitted.
	 * @param hanlder a user-defined function that is called each time an answer is submitted.
	 */
	api_.onAnswerSubmitted = function(handler){
		if (handler && $.type(handler) === "function")
			answerSubmitted = handler;
	};
	/**
	 * Returns the current question's identifier.
	 */
	api_.getCurrentQuestion = function(){
		return progress_[progress_.length - 1];
	};
	/**
	 * Set a user-defined function that returns the identifier of the next question to present.
	 * @param hanlder a user-defined function that determines the questionnaire flow.
	 */
	api_.onGetNextQuestion = function(handler){
		if (handler && $.type(handler) === "function")
			getNextQuestion = handler;
	};
	/**
	 * Set a user-defined function that displays the next question.
	 * @param hanlder a user-defined function that displays the next question.
	 */
	api_.onShowNextQuestion = function(handler){
		if (handler && $.type(handler) === "function")
			showNextQuestion = handler;
	};
	/**
	 * Displays the specified question.
	 * Note that since question IDs are sequential, we assume the questionnaire
	 * is completed when the specified question ID is greater than the number
	 * questions, at which point a submit button is displayed.
	 * @param question a positive integer used to identify a question.
	 */
	api_.showQuestion = function(question){
		// If at least one question has been answered, hide the current question
		// before moving onto the next. Update the rewind button too.
		var hasAnsweredQuestion = progress_.length > 0;
		if (hasAnsweredQuestion)
			getCurrentQuestionElement().addClass("hide");

		$("#questionnaire-rewind").prop("disabled", !hasAnsweredQuestion);

		if (question >= initialQuestion_){
			// Update the progress stack.
			progress_.push(question);

			// Update the status panel. Remember that when the questionnaire is
			// complete, a submit button is displayed in the status panel.
			updateStatus();

			// If we haven't completed the questionnaire yet, display the next question.
			if (question < (initialQuestion_ + numberOfQuestions_)){
				var $element = getQuestionElement(question);
				$element.removeClass("hide").hide().fadeIn(300, function(){
					// If the question type is geotagging, then we need to resize the map only when the question is
					// made visible, so that the OpenLayers API uses the correct dimensions.
					if ($element.data("type") === "geotagging" && olMap_ != null)
						olMap_.updateSize();
				});

				// Update analytics parameters.
				geotagx.analytics.onQuestionChanged(question);
			}
		}
		else
			console.log("[geotagx::questionnaire::showQuestion] Error! Invalid question identifier '" + question + "'.");
	};
	/**
	 * Finishes a project task.
	 * This function will skip any remaining questions and display the user's input summary, their current statistics, as well as a submit button.
	 */
	api_.finish = function(){
		// Since the question IDs are distributed sequentially, the questionnaire
		// is considered finished when the current question  ID is greater than
		// or equal to the total number of questions plus the initial question's ID.
		api_.showQuestion(initialQuestion_ + numberOfQuestions_);
	};

	geotagx.questionnaire = api_;
})(window.geotagx = window.geotagx || {}, jQuery);
