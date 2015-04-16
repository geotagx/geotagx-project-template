/* Define a custom script for your project here. */


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
	 * Returns the answer submitted by the specified submitter.
	 */
	function getAnswer(questionType, $submitter){
		var answer = $submitter.attr("value");
		if (questionType === "multiple-choice" && answer === "Done"){
			// When the question is multiple-choice, the actual answer is contained in the
			// set of selected input elements. A non-empty set is converted into a string
			// containing each input value, while an empty set is converted into the string 'None'.
			var $input = $submitter.siblings("input:checked");
			if ($input.length === 0)
				answer = "None";
			else {
				answer = "";
				$input.each(function(){
					answer += ", " + $(this).val();
				});
				answer = answer.substring(2); // Remove the leading comma and space.
			}
		}

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
	/*
     * Returns the specified question's HTML node.
     */
    function getQuestionElement(question){
        return $(getQuestionNodeId(question));
    }
	/*
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

            // If the question identifier is equal to the total number of questions, then display the user's answer card.
            if (isSubmissionForm(question)){
                console.log("Showing answer card...");
				console.log(taskRun_);
        /*
                var $currentQuestionHtml = getCurrentQuestionElement();
                var $rewindButton = $("#questionnaire-rewind");
                // var $summary = $("#questionnaire-summary");

                // Hide the current question and enable the rewind button.
                $currentQuestionHtml.addClass("hide");
                $rewindButton.prop("disabled", false);

                // $summary.collapse("show");


                // $answerCard.addClass("expanded");
                // $answerCard.removeClass("collapsed");
        */

        // $("#questionnaire-answers").collapse("show");
        // setTimeout(function(){ $("#questionnaire-answers").collapse("hide") }, 1000);

        /*
        if (percentageComplete_ >= 100){
            $("#questionnaire-submit").removeClass("hide");
            $("#questionnaire-conclusion").removeClass("hide");
            $("#questionnaire-answers").collapse();
        }
        else {
            $("#questionnaire-submit").addClass("hide");
            $("#questionnaire-conclusion").addClass("hide");
        }
        */
            }
            else {
				getCurrentQuestionElement().removeClass("hide").hide().fadeIn(300);
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

				// Set the submission button's handler. Note that off().on() resets the
				// click event handler every time a new task is loaded.
				$("#questionnaire-submit").off("click").on("click", function(){
					console.log("Saving result...");
					console.log(taskRun_);

					// var $button = $(this);
					//
					// pybossa.saveTask(taskRun_.id, taskRun_).done(function(){
					// 	deferred.resolve();
					// 	$button.prop("disabled", false);
					// });
				});

                $(".btn-answer").off("click").on("click", function(){
					var $submitter = $(this);
					var question = getCurrentQuestion();
					var questionType = getQuestionType(question);
					var answer = getAnswer(questionType, $submitter);

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

                // $("#loading").hide();
            }
            else {
                // $(".skeleton").hide();
                // $("#loading").hide();
                // $("#finish").fadeIn(500);
            }
        });

        // Run the task.
        pybossa.run(slug);
	};

	geotagx.task = task_;
})(window.geotagx = window.geotagx || {}, jQuery);


/*!
	Wheelzoom 3.0.0
	license: MIT
	http://www.jacklmoore.com/wheelzoom
*/
window.wheelzoom = (function(){
	var defaults = {
		zoom: 0.10
	};
	var canvas = document.createElement('canvas');

	function setSrcToBackground(img) {
		img.style.backgroundImage = "url('"+img.src+"')";
		img.style.backgroundRepeat = 'no-repeat';
		canvas.width = img.naturalWidth;
		canvas.height = img.naturalHeight;
		img.src = canvas.toDataURL();
	}

	main = function(img, options){
		if (!img || !img.nodeName || img.nodeName !== 'IMG') { return; }

		var settings = {};
		var width;
		var height;
		var bgWidth;
		var bgHeight;
		var bgPosX;
		var bgPosY;
		var previousEvent;

		function updateBgStyle() {
			if (bgPosX > 0) {
				bgPosX = 0;
			} else if (bgPosX < width - bgWidth) {
				bgPosX = width - bgWidth;
			}

			if (bgPosY > 0) {
				bgPosY = 0;
			} else if (bgPosY < height - bgHeight) {
				bgPosY = height - bgHeight;
			}

			img.style.backgroundSize = bgWidth+'px '+bgHeight+'px';
			img.style.backgroundPosition = bgPosX+'px '+bgPosY+'px';
		}

		function reset() {
			bgWidth = width;
			bgHeight = height;
			bgPosX = bgPosY = 0;
			updateBgStyle();
		}

		function onwheel(e) {
			var deltaY = 0;

			e.preventDefault();

			if (e.deltaY) { // FireFox 17+ (IE9+, Chrome 31+?)
				deltaY = e.deltaY;
			} else if (e.wheelDelta) {
				deltaY = -e.wheelDelta;
			}

			// As far as I know, there is no good cross-browser way to get the cursor position relative to the event target.
			// We have to calculate the target element's position relative to the document, and subtrack that from the
			// cursor's position relative to the document.
			var rect = img.getBoundingClientRect();
			var offsetX = e.pageX - rect.left - document.body.scrollLeft;
			var offsetY = e.pageY - rect.top - document.body.scrollTop;

			// Record the offset between the bg edge and cursor:
			var bgCursorX = offsetX - bgPosX;
			var bgCursorY = offsetY - bgPosY;

			// Use the previous offset to get the percent offset between the bg edge and cursor:
			var bgRatioX = bgCursorX/bgWidth;
			var bgRatioY = bgCursorY/bgHeight;

			// Update the bg size:
			if (deltaY < 0) {
				bgWidth += bgWidth*settings.zoom;
				bgHeight += bgHeight*settings.zoom;
			} else {
				bgWidth -= bgWidth*settings.zoom;
				bgHeight -= bgHeight*settings.zoom;
			}

			// Take the percent offset and apply it to the new size:
			bgPosX = offsetX - (bgWidth * bgRatioX);
			bgPosY = offsetY - (bgHeight * bgRatioY);

			// Prevent zooming out beyond the starting size
			if (bgWidth <= width || bgHeight <= height) {
				reset();
			} else {
				updateBgStyle();
			}
		}

		function drag(e) {
			e.preventDefault();
			bgPosX += (e.pageX - previousEvent.pageX);
			bgPosY += (e.pageY - previousEvent.pageY);
			previousEvent = e;
			updateBgStyle();
		}

		function removeDrag() {
			document.removeEventListener('mouseup', removeDrag);
			document.removeEventListener('mousemove', drag);
		}

		// Make the background draggable
		function draggable(e) {
			e.preventDefault();
			previousEvent = e;
			document.addEventListener('mousemove', drag);
			document.addEventListener('mouseup', removeDrag);
		}

		function loaded() {
			var computedStyle = window.getComputedStyle(img, null);

			width = parseInt(computedStyle.width, 10);
			height = parseInt(computedStyle.height, 10);
			bgWidth = width;
			bgHeight = height;
			bgPosX = 0;
			bgPosY = 0;

			setSrcToBackground(img);

			img.style.backgroundSize =  width+'px '+height+'px';
			img.style.backgroundPosition = '0 0';
			img.addEventListener('wheelzoom.reset', reset);

			img.addEventListener('wheel', onwheel);
			img.addEventListener('mousedown', draggable);
		}

		img.addEventListener('wheelzoom.destroy', function (originalProperties) {
			console.log(originalProperties);
			img.removeEventListener('wheelzoom.destroy');
			img.removeEventListener('wheelzoom.reset', reset);
			img.removeEventListener('load', onload);
			img.removeEventListener('mouseup', removeDrag);
			img.removeEventListener('mousemove', drag);
			img.removeEventListener('mousedown', draggable);
			img.removeEventListener('wheel', onwheel);

			img.style.backgroundImage = originalProperties.backgroundImage;
			img.style.backgroundRepeat = originalProperties.backgroundRepeat;
			img.src = originalProperties.src;
		}.bind(null, {
			backgroundImage: img.style.backgroundImage,
			backgroundRepeat: img.style.backgroundRepeat,
			src: img.src
		}));

		options = options || {};

		Object.keys(defaults).forEach(function(key){
			settings[key] = options[key] !== undefined ? options[key] : defaults[key];
		});

		if (img.complete) {
			loaded();
		} else {
			function onload() {
				img.removeEventListener('load', onload);
				loaded();
			}
			img.addEventListener('load', onload);
		}
	};

	// Do nothing in IE8
	if (typeof window.getComputedStyle !== 'function') {
		return function(elements) {
			return elements;
		}
	} else {
		return function(elements, options) {
			if (elements && elements.length) {
				Array.prototype.forEach.call(elements, main, options);
			} else if (elements && elements.nodeName) {
				main(elements, options);
			}
			return elements;
		}
	}
}());

// Run the application.
geotagx.task.run("geotagx-project-sample", function(question, answer){
    geotagx.task.showNextQuestion();
});
