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
    var onAnswerSubmitted_ = function(){}; // A function that's called each time the user submits an answer to a question.

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
			if (property){
				taskRun_[property] = null;
			}
		});
	});
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
	/*
     * Returns the specified question's HTML node.
     */
    function getQuestionHtml(question){
        return $(getQuestionNodeId(question));
    }
	/*
     * Returns the current question's HTML node.
     */
    function getCurrentQuestionHtml(){
        return getQuestionHtml(getCurrentQuestion());
    }
	/**
	 *
	 */
	function updateProgress(){
		percentageComplete_ = progress_.length > 0 ? ((getCurrentQuestion() / numberOfQuestions_) * 100).toFixed(0) : 0;

        $("#questionnaire-percentage-complete").html(percentageComplete_);
        $("#questionnaire-progress-bar").css("width", percentageComplete_ + "%");
	};
	/*
     * Returns true if the question identifier refers to the spam filter, false otherwise.
     */
    function isSpamFilter(question){
        return question === 0;
    }
    /*
     * Returns true if the question identifier refers to the submission form, false otherwise.
     */
    function isSubmissionForm(question){
        return question === numberOfQuestions_;
    }
	/*
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
    /*
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
	 * Begins a new task.
	 * This function also resets the progress stack as well as all input to prevent corrupting
	 * results from later tasks.
	 */
	function beginTask(){
		$("input:checkbox").removeAttr("checked"); // Reset all input fields.
        $(".question").addClass("hide");
        progress_ = [];

        // Reset the current task run.
        for (var property in taskRun_)
			taskRun_[property] = null;

		task_.showQuestion(0); // Note: 0 is the spam filter.
	};
	/*
     * A slightly modified version of the throttle function taken from the Underscore.js 1.8.2 library (http://underscorejs.org).
     * (c) 2009-2015 Jeremy Ashkenas, DocumentCloud and Investigative Reporters & Editors
     *
     * Returns a function, that, when invoked, will only be triggered at most once
     * during a given window of time. Normally, the throttled function will run
     * as much as it can, without ever going more than once per `wait` duration;
     * but if you'd like to disable the execution on the leading edge, pass
     * `{leading: false}`. To disable execution on the trailing edge, ditto.
     */
    function throttle(func, wait, options){
        var context,
            args,
            result,
            timeout = null,
            previous = 0,
            _now = Date.now || function(){ return new Date().getTime(); }; // A (possibly faster) way to get the current timestamp as an integer.

        if (!options)
            options = {};

        var later = function(){
            previous = options.leading === false ? 0 : _now();
            timeout = null;
            result = func.apply(context, args);
            if (!timeout)
                context = args = null;
        };

        return function(){
            var now = _now();
            if (!previous && options.leading === false)
                previous = now;

            var remaining = wait - (now - previous);
            context = this;
            args = arguments;

            if (remaining <= 0 || remaining > wait){
                if (timeout){
                    clearTimeout(timeout);
                    timeout = null;
                }
                previous = now;
                result = func.apply(context, args);
                if (!timeout)
                    context = args = null;
            }
            else if (!timeout && options.trailing !== false){
                timeout = setTimeout(later, remaining);
            }
            return result;
        };
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
			if (property){
				var typeofAnswer = $.type(answer);

				if (typeofAnswer === "undefined")
					answer = null;
				else if (typeofAnswer === "object"){
					// When the answer is an object, it is assumed to be a collection of input elements. A non-empty collection is
					// converted into a string containing each input values, while an empty collection is converted into the string 'None'.
					if (answer.length > 0){
						var tmp = "";
						answer.each(function(){
							tmp += "," + $(this).val();
						});
						answer = tmp.substring(1); // Remove the leading comma.
					}
					else
						answer = "None";
				}
				taskRun_[property] = answer;
			}
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
			getCurrentQuestionHtml().addClass("hide");

        // If we have a valid question id ...
        if (question >= 0 && question <= numberOfQuestions_){
            // Update the progress stack and progress bar.
            progress_.push(question);
            updateProgress();

            // If the question identifier is equal to the total number of questions, then display the user's answer card.
            if (isSubmissionForm(question)){
                console.log("Showing answer card...");
				console.log(taskRun_);

                if (percentageComplete_ >= 100){
                    $("#questionnaire-submit").show()
                    $("#questionnaire-conclusion").show();
                }
                else {
                    $("#questionnaire-submit").hide();
                    $("#questionnaire-conclusion").hide();
                }
                
            }
            else {
				getCurrentQuestionHtml().removeClass("hide").hide().fadeIn(300);
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

            // Remove the previous entry from the answer card.
            removeAnswerCardEntry(previous);

            // Update the progress stack and progress bar.
            progress_.pop();
            updateProgress();

            // Disable the rewind button if there're no more previous questions.
            if (progress_.length === 1)
                $("#questionnaire-rewind").prop("disabled", true);

            // Hide the current question and show the previous.
            getQuestionHtml(previous).removeClass("hide");
			getQuestionHtml(current).addClass("hide");
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
	 * @param project the project's name.
	 * @param onAnswerSubmitted a function object that's called each time the user submits an answer to a question.
	 */
	task_.run = function(project, onAnswerSubmitted){
		if ($.type(project) !== "string" || $.type(onAnswerSubmitted) !== "function"){
            console.log("[geotagx::task::run] Error! Invalid function parameter.");
            return;
        }

		onAnswerSubmitted_ = onAnswerSubmitted;

        pybossa.taskLoaded(function(task, deferred){
            if (!$.isEmptyObject(task)){
                var $image = $("<img/>");
                $image.load(function(){
                    deferred.resolve(task);
                });
                $image.attr('src', task.info.url);
                $image.attr('id', 'anno_' + task.id);
                $image.addClass('img-polaroid');
                $image.addClass('annotable');

                task.info.image = $image;

                // Append PyBossa-related properties to the task result.
                taskRun_.task_id = task.id;
                taskRun_.img = task.info.url;
            }
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
                    $image.attr("src", task.info.url);
                    $image.addClass("highlight");
                    $image.addClass("wheelzoom");

                    $("#image-source").attr("href", task.info.uri); // Note URI and not URL.
                    $("#image-loading").addClass("hide");

                    wheelzoom($image);
                }
                else
                    console.log("[pybossa::presentTask] Error! Could not find image to analyze.");

                $("#questionnaire-show-comments").prop("disabled", false);

                // Reset user input and the task run when a new task is presented.
                beginTask();

                // Set the answer button event handlers.
                // $(".btn-answer").off("click").on("click", function(){                            // TODO Make sure this was not a better solution.
                $(".btn-answer").click(throttle(function(){
                    var $submitter = $(this);
                    var answer = $submitter.attr("value");
                    var question = getCurrentQuestion();
                    var questionHtml = getQuestionHtml(question);

                    if (isSpamFilter(question)){
                        if (answer === "No")
                            geotagx.task.showNextQuestion(); // The image is not spam, proceed to the first question.
                        else
                            geotagx.task.finish();
                    }
                    else if ($submitter.attr("id") === "questionnaire-submit"){
						var $button = $(this);
						$button.prop("disabled", true);

                        console.log("Saving result...");
                        console.log(taskRun_);

                        pybossa.saveTask(task.id, taskRun_).done(function(){
                            deferred.resolve();
							$button.prop("disabled", false);

                            $("#questionnaire-submit").hide(); //Hide the Submit Button
                            $("#questionnaire-conclusion").hide(); //hide the conclusion
                        });

                    }
                    else {
                        //TO-DO :: Preprocess stuff here based on question class
                        onAnswerSubmitted_(question, answer, $submitter);
                    }
                    addAnswerCardEntry(question, answer);
                }, 800));


                // $("#loading").hide();
            }
            else {
                // $(".skeleton").hide();
                // $("#loading").hide();
                // $("#finish").fadeIn(500);
            }
        });

        // Run the task.
        pybossa.run(project);
	};

	geotagx.task = task_;
})(window.geotagx = window.geotagx || {}, jQuery);
