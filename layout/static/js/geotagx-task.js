/*
 * The GeoTag-X task helper.
 * TODO Add license.
 * TODO Add authors.
 *
 * - finish completes a task and presents the user's results, summary and a submission button.
 * - saveAnswer stores the answer to the current question.
 * - showNextQuestion displays the next question.
 * - showPreviousQuestion displays the previous question.
 * - showQuestion displays the specified question.
 * - run initializes the project and executes the initial task.
 */
(function(geotagx, $, undefined){
	"use strict";

	var task_ = {}; // The GeoTag-X task helper object.
	var taskRun_ = {}; // The results to submit for the current task.
    var numberOfQuestions_ = 0; // The number of questions asked in this project, including the spam filter.
    var percentageComplete_ = 0; // The percentage of questions completed.
    var progress_ = []; // A stack used to track the user's progress throughout a task. More specifically, it allows a user to rewind to a previous question.
    var onShowNextQuestion_ = function(){}; // A user-defined function that determines the next question presented to the user.
	var olMap_ = null; // The OpenLayers 3 map instance.

	$(document).ready(function(){
		numberOfQuestions_ = $(".question").length;

		$("#questionnaire-rewind").click(task_.showPreviousQuestion);
		$("*[data-toggle=tooltip]").tooltip();

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

		// Initialize the taskRun_ object's properties. A property is located in each
		// element with the 'answer' class, that has a non-empty 'saved-as' data attribute.
		$(".answer").each(function(){
			var property = $.trim($(this).data("saved-as"));
			if (property)
				taskRun_[property] = null;
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
	 * Returns the answer submitted by the specified submitter.
	 */
	function getAnswer(questionType, $submitter){
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
	 * Returns the current question.
	 */
	function getCurrentQuestion(){
		return progress_[progress_.length - 1];
	}
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
		return getQuestionNodeId(getCurrentQuestion());
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
        return getQuestionElement(getCurrentQuestion());
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
		percentageComplete_ = progress_.length > 0 ? (((getCurrentQuestion() - 1) / (numberOfQuestions_ - 1)) * 100).toFixed(0) : 0;

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
    function isQuestionnaireCompleted(question){
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
     * Displays the complete questionnaire summary if show is set to true, otherwise shows the compact version.
     */
    function showFullQuestionnaireSummary(show){
		if (show)
			$("#questionnaire-summary").removeClass("minimized");
		else
			$("#questionnaire-summary").addClass("minimized");


		if (show) console.log(taskRun_); /*TODO: Remove when done debugging.*/
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
	 * Begins a new task.
	 * This function also resets the progress stack as well as all input to prevent corrupting
	 * results from later tasks.
	 */
	function beginTask(){
		resetInput();

        $(".question").addClass("hide");
        progress_ = [];

		// Reset the answer card.
		$("#questionnaire-answer-card").empty();

        // Reset the current task run.
        for (var property in taskRun_)
			taskRun_[property] = null;

		// task_.showQuestion(0); // Note: question 0 is the spam filter.
		task_.showQuestion(1);
	};
	/**
	 * Saves the current question's answer.
	 * @param answer the answer to save.
	 */
	task_.saveAnswer = function(answer){
		// Save an answer to its corresponding 'saved-as' field.
		var htmlNodeId = getCurrentQuestionNodeId();
		if (htmlNodeId){
			var property = $(htmlNodeId + " > div.answer").data("saved-as");
			if (property)
				taskRun_[property] = $.type(answer) === "undefined" ? null : answer;
			else
				console.log("[geotagx::task::saveAnswer] Could not find a 'saved-as' data attribute. Discarding answer...");
		}
	};
	/**
	 * Displays the specified question.
	 * @param question a positive integer used to identify a question.
	 */
	task_.showQuestion = function(question){
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
            if (isQuestionnaireCompleted(question))
				showFullQuestionnaireSummary(true);
            else {
				var $element = getQuestionElement(question);
				$element.removeClass("hide").hide().fadeIn(300, function(){
					// If the question type is geotagging, then we need to resize the map only when the question is
					// made visible, so that the OpenLayers API uses the correct dimensions.
					if ($element.data("type") === "geotagging" && olMap_ != null)
						olMap_.updateSize();
				});
			}
        }
        else
            console.log("[geotagx::task::showQuestion] Error! Invalid question identifier '" + question + "'.");
	};
	/**
	 * Displays the next question.
	 * If no more questions are left, the user's input summary and a submit button are displayed instead.
	 */
	task_.showNextQuestion = function(){
		task_.showQuestion(getCurrentQuestion() + 1);
	};
	/**
	 * Displays the previous question, iff it exists.
	 */
	task_.showPreviousQuestion = function(){
		// We can only rewind if we've completed at least two questions.
        if (progress_.length >= 2){
            var current  = progress_[progress_.length - 1];
            var previous = progress_[progress_.length - 2];

            // Destroy the current result before loading the previous question.
            task_.saveAnswer(null);

            // Minimize the information displayed on the questionnaire summary.
            if (isQuestionnaireCompleted(current))
				showFullQuestionnaireSummary(false);

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
        }
        else
            console.log("[geotagx::task::showPrevQuestion] Error! Could not load the previous question!");
	};
	/**
	 * Finishes a project task.
	 * This function will skip any remaining questions and display the user's input summary, their current statistics, as well as a submit button.
	 */
	task_.finish = function(){
		// The task is considered finished when the current question is equal to the total number of questions.
		task_.showQuestion(numberOfQuestions_);
	};
	/**
	 * Runs the project's initial task.
	 * @param slug the project's short name.
	 * @param onShowNextQuestion a user-defined function that returns the id of the next question to present to the user.
	 */
	task_.run = function(slug, onShowNextQuestion){
		if ($.type(slug) !== "string" || $.type(onShowNextQuestion) !== "function"){
            console.log("[geotagx::task::run] Error! Invalid function parameter.");
            return;
        }

		onShowNextQuestion_ = onShowNextQuestion;

        pybossa.taskLoaded(function(task, deferred){
            if (!$.isEmptyObject(task))
				$("<img/>").load(function(){ deferred.resolve(task); }).attr("src", task.info.image_url);
            else
                deferred.resolve(task);
        });

        pybossa.presentTask(function(task, deferred){
            if (!$.isEmptyObject(task)){
                // Show/hide respective elements.
                $(".show-on-task-loaded").removeClass("show-on-task-loaded").hide().fadeIn(200);
                $(".hide-on-task-loaded").hide();

                // Initialize the image to analyze.
                var $image = $("#image");
                if ($image.length > 0){
                    $image.attr("src", task.info.image_url);

                    $("#image-source").attr("href", task.info.source_uri);

                    wheelzoom($image);
                }
                else
                    console.log("[pybossa::presentTask] Error! Could not find image to analyze.");

                $("#questionnaire-show-comments").prop("disabled", false);

				// Set the submission button's handler. Note that off().on() removes the previous handler
				// and sets a new one, every time a new task is loaded. This prevents a chain of events
				// being called when a button is pushed once.
				$("#questionnaire-submit").off("click.task").on("click.task", function(){
					var $button = $(this);
					$button.prop("disabled", true);

					// Append the image URL to the saved result.
					taskRun_.img = task.info.image_url;

					pybossa.saveTask(task.id, taskRun_).done(function(){
						showFullQuestionnaireSummary(false);
						$button.prop("disabled", false);
						deferred.resolve();
					});
				});

                $(".btn-answer").off("click.task").on("click.task", function(){
					var $submitter = $(this);
					var question = getCurrentQuestion();
					var answer = getAnswer(getQuestionType(question), $submitter);

                    if (isSpamFilter(question)){
                        if (answer === "No")
                            task_.showNextQuestion(); // The image is not spam, proceed to the first question.
                        else
							task_.finish();
                    }
                    else {
						task_.saveAnswer(answer);
						onShowNextQuestion_(question, answer);
                    }

                    addAnswerCardEntry(question, answer);
                });

				// Reset user input and the task run when a new task is presented.
				beginTask();
            }
        });

        // Run the task.
        pybossa.run(slug);
	};

	geotagx.task = task_;
})(window.geotagx = window.geotagx || {}, jQuery);
