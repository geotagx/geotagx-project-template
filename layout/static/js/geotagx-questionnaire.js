/*
 * The GeoTag-X questionnaire helper.
 */
(function(geotagx, $, undefined){
	"use strict";

	var api_ = {}; // The questionnaire API.
	var answers_ = {}; // The questionnaire's answers.
    var numberOfQuestions_ = 0; // The number of questions asked in this project, including the spam filter.
	var initialQuestion_ = 0; // The questionnaire's initial question.
    var percentageComplete_ = 0; // The percentage of questions completed.
    var progress_ = []; // A stack used to track the user's progress throughout the questionnaire. It also allows a user to rewind to a previous question.
	var olMap_ = null; // The OpenLayers 3 map instance.

	$(document).ready(function(){
		numberOfQuestions_ = $(".question").length;

		$("*[data-toggle=tooltip]").tooltip();
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

		// Set the summary details button handler.
		$("#questionnaire-summary-details").click(function(){
			// Toggle the expanded attribute to either 'true' or 'false' which will determine whether
			// to display 'Show' or 'Hide' text (or the respective icons).
			$(this).attr("aria-expanded", $(this).attr("aria-expanded") === "true" ? "false" : "true");
		});

		// Set answer button handlers.
		$(".btn-answer").on("click.questionnaire", function(){
			var $submitter = $(this);
			var question = api_.getCurrentQuestion();
			var answer = parseAnswer(getQuestionType(question), $submitter);

			// Save the answer.
			var storageKey = getStorageKey(question);
			if (storageKey)
				saveAnswer(storageKey, answer);

			showNextQuestion(question, answer, $submitter);
		});

		// Initialize the answers_ object's properties. A property is located in each
		// element with the 'answer' class, that has a non-empty 'saved-as' data attribute.
		$(".answer").each(function(){
			var property = $.trim($(this).data("saved-as"));
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
							view.setCenter(ol.proj.transform([result.lon, result.lat], "EPSG:4326", "EPSG:900913"));
							view.setZoom(4);

							console.log(result);



/*
	                        var result         = results[0];
	                        var fromProjection = new OpenLayers.Projection("EPSG:4326"); // Transform from WGS 1984 ...
	                        var toProjection   = new OpenLayers.Projection("EPSG:900913"); // ... to Spherical Mercator.
	                        var coordinates    = new OpenLayers.LonLat(result.lon, result.lat).transform(fromProjection, toProjection);
	                        var zoomFactor     = 10;
*/
	                    }
	                    else
	                        console.log("Location not found!"); // e.g. xyxyxyxyxyxyx
					});
	            }
	        });
		}
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
		if (isSpamFilter(question)){
			if (answer === "no")
				api_.showQuestion(question + 1); // The content to analyze is not spam, proceed to the first question.
			else
				api_.finish();
		}
		else
			api_.showQuestion(getNextQuestion(question, answer));

		//addAnswerCardEntry(question, answer);									/*FIXME Fix answer card. */
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

            // Minimize the information displayed on the questionnaire summary.
            if (isCompleted(current))
				api_.showFullSummary(false);

            // Remove the previous entry from the answer card.
            removeAnswerCardEntry(previous);

            // Update the progress stack and progress bar.
            progress_.pop();
            updateProgress();

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
		function inputToString($input){
			var output = "";
			$input.each(function(){
				output += ", " + $(this).val();
			});
			return output.substring(2); // Remove the leading comma and space.
		}

		var answer = $submitter.attr("value");
		if (answer === "Done"){
			switch (questionType){
				case "single_choice":
					var $input = $("input:checked", $submitter.siblings("label"));
					return $input.length > 0 ? $input.val() : "None";
				case "multiple_choice":
					var $input = $("input:checked", $submitter.siblings("label"));
					return $input.length > 0 ? inputToString($input) : "None";
				case "illustrated_multiple_choice":
					var $illustrations = $(".illustration", $submitter.parent().siblings(".illustrations"));
					var $input = $("input[type='checkbox']:checked", $illustrations);

					answer = $.trim($("input[type='text']", $illustrations).val()); // The user's unlisted answer.
					answer =
					answer ? ($input.length === 0 ? answer : answer + ", " + inputToString($input))
					       : ($input.length === 0 ? "None" : inputToString($input));

					return answer;
				case "geotagging":
					return getMapSelection();
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
		if (storageKey){
			answers_[storageKey] = $.type(answer) === "undefined" ? null : answer;
		}
		else
			console.log("[geotagx::questionnaire::saveAnswer] Error! Invalid storage key. Answer discarded...");
	};
	/**
	 * Returns the specified question's HTML node identifier.
	 */
	function getQuestionNodeId(question){
		return question > 0 && question < numberOfQuestions_ ? "#questionnaire-question-" + question : question === 0 ? "#questionnaire-filter" : null;
	}
	/**
	 * Returns the current question's HTML node identifier.
	 */
	function getCurrentQuestionNodeId(){
		return getQuestionNodeId(api_.getCurrentQuestion());
	}
	/**
	 * Returns the specified question's HTML node.
	 */
	function getQuestionElement(question){
		return $(getQuestionNodeId(question));
	}
	/**
	 * Returns the current question's HTML node.
	 */
	function getCurrentQuestionElement(){
		return getQuestionElement(api_.getCurrentQuestion());
	}
	/**
	 * Returns the type of the specified question.
	 */
	function getQuestionType(question){
		return getQuestionElement(question).data("type");
	}
	/**
	 * Updates the progress bar and percentage.
	 */
	function updateProgress(){
		percentageComplete_ = progress_.length > 0 ? (((api_.getCurrentQuestion() - initialQuestion_) / (numberOfQuestions_ - initialQuestion_)) * 100).toFixed(0) : 0;

		$("#questionnaire-percentage-complete").html(percentageComplete_);
		$("#questionnaire-progress-bar").css("width", percentageComplete_ + "%");
	};
	/**
	 * Returns true if the question identifier refers to the spam filter, false otherwise.
	 */
	function isSpamFilter(question){
		return question === 0;
	}
	/**
	 * Returns true if the questionnaire has been completed, false otherwise.
	 * A questionnaire is considered complete if the question identifier is equal to the total number of questions.
	 */
	function isCompleted(question){
		return question === numberOfQuestions_;
	}
	/**
	 * Adds an entry to the user's answer card.
	 */
	function addAnswerCardEntry(questionId, answer){
		var $answerCard = $("#questionnaire-answer-card");
		if ($answerCard.length > 0){
			var nodeId = getQuestionNodeId(questionId);
			if (nodeId){
				var question = $(nodeId + " > header").html();
				if (question){
					var entry = '<li id="questionnaire-answer-card-entry-' + questionId + '">' + question + ' ' + answer + '</li>';
					$(entry).hide().appendTo("#questionnaire-answer-card").fadeIn(200);
				}
			}

			// Enable the summary details button.
			var numberOfEntries = $("li", $answerCard).length;
			if ($("#questionnaire-summary-details").hasClass("hide") && numberOfEntries > 0)
				$("#questionnaire-summary-details").removeClass("hide").hide().fadeIn();
		}
	}
	/**
	 * Removes the specified question's entry from the user's answer card.
	 */
	function removeAnswerCardEntry(question){
		setTimeout(function(){
			var $answerCard = $("#questionnaire-answer-card");

			$("#questionnaire-answer-card-entry-" + question).fadeOut(200, function(){
				$(this).remove();

				var numberOfEntries = $("li", $answerCard).length;
				if (!$("#questionnaire-summary-details").hasClass("hide") && numberOfEntries == 0)
					$("#questionnaire-summary-details").fadeOut(80, function(){ $(this).addClass("hide"); });
			});
		}, 150);
	}
	/**
	 * Resets all user input.
	 */
	function resetInput(){
		$("input").removeAttr("checked");
		$("input:text").val("");

		resetMap(true);
	}
	/**
	 * Returns the storage key for the specified question, or null if it doesn't exist.
	 * A storage key is stored in the question's answer div as the "saved-as" data attribute.
	 */
	function getStorageKey(question){
		var key = null;
		var nodeId = getQuestionNodeId(question);
		if (nodeId){
			var field = $(nodeId + " > div.answer").data("saved-as");
			key = field ? field : null;
		}
		return key;
	}
	/**
	 * Starts the questionnaire from the specified question.
	 */
	api_.start = function(question){
		$(".question").addClass("hide");

		resetInput();
		progress_ = [];

		// Reset the answer card and enable comments.
		$("#questionnaire-answer-card").empty();
		$("#questionnaire-show-comments").prop("disabled", false);

		// Reset the current task run.
		for (var property in answers_)
			answers_[property] = null;

		// Toggle wheelzoom on the image.
		wheelzoom($("#image"));

		// Determine the first question.
		initialQuestion_ = question && $.type(question) === "number" ? question : 0;

		api_.showQuestion(initialQuestion_);
	};
	/**
	 * Returns the number of questions.
	 */
	api_.getNumberOfQuestions = function(){
		return numberOfQuestions_;
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
	 * Displays the complete questionnaire summary if show is set to true, otherwise shows the compact version.
	 */
	api_.showFullSummary = function(show){
		if (show)
			$("#questionnaire-summary").removeClass("minimized");
		else
			$("#questionnaire-summary").addClass("minimized");
																					if (show) console.log(answers_); /*TODO: Remove when done debugging.*/
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
	 * @param question a positive integer used to identify a question.
	 */
	api_.showQuestion = function(question){
		console.log("Showing question " + question);

		var hasAnsweredQuestion = progress_.length > 0;

		// Enable the rewind button if the user has at least one answered question, disable it otherwise.
		$("#questionnaire-rewind").prop("disabled", !hasAnsweredQuestion);

		// Hide the current question since we'll be moving onto the next.
		if (hasAnsweredQuestion)
			getCurrentQuestionElement().addClass("hide");

		// If we have a valid question id ...
		if (question >= 0 && question <= numberOfQuestions_){
			// Update the progress stack and progress bar.
			progress_.push(question);
			updateProgress();

			// If the questionnaire has been completed, display the full questionnaire summary.
			// If it hasn't, show the next question.
			if (isCompleted(question))
				api_.showFullSummary(true);
			else {
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
		// The task is considered finished when the current question is equal to the total number of questions.
		api_.showQuestion(numberOfQuestions_);
	};

	geotagx.questionnaire = api_;
})(window.geotagx = window.geotagx || {}, jQuery);
