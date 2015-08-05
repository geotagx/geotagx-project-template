/*
 * The GeoTag-X tutorial helper.
 */
;(function(geotagx, $, undefined){
	"use strict";

	var api_ = {}; // The tutorial API.
	var numberOfTutorials_ = 0; // The number of available tutorials.
	var currentTutorial_ = 0; // The index of the current tutorial.
	var assertions_ = null; // An object containing assertions about the image being analyzed.
	var nextQuestion_ = 0; // The next question's identifier.
	var getNextQuestion_ = null; // A user-defined function that determines the next question.

	/**
	 * Begins the project tutorial.
	 * @param shortName the project's short name.
	 * @param getNextQuestion a user-defined function that returns the id of the next question to present to the user.
	 * @param tutorial an array of objects containing a link to an image, and assertions about the image.
	 */
	api_.start = function(shortName, getNextQuestion, tutorial){
		if ($.type(shortName) !== "string"){
			console.log("[geotagx::project::start] Error! Invalid project slug.");
			return;
		}

		getNextQuestion_ = getNextQuestion;
		numberOfTutorials_ = tutorial.length;
		currentTutorial_ = Math.floor((Math.random() * numberOfTutorials_)); // Select a random tutorial out of all available ones.
		setTutorial(tutorial[currentTutorial_]);

		geotagx.questionnaire.onShowNextQuestion(onShowNextQuestion);
		geotagx.questionnaire.onQuestionChanged(onQuestionChanged);

		$(".show-on-task-loaded").removeClass("show-on-task-loaded").hide().fadeIn(200);
		$(".hide-on-task-loaded").hide();
		$("#questionnaire-rewind").on("click.tutorial", function(){
			hideNotification();
		});
		$("#tutorial-next-question").on("click.tutorial", function(){
			hideNotification(function(){ geotagx.questionnaire.showQuestion(nextQuestion_) });
		});
		$("#take-another-tutorial").on("click.tutorial", function(){
			currentTutorial_ = (currentTutorial_ + 1) % numberOfTutorials_;
			setTutorial(tutorial[currentTutorial_]);
			geotagx.questionnaire.start();
		});
		geotagx.questionnaire.start();
	};

	function setTutorial(tutorial){
		var $image = $("#image");
		if ($image.length > 0){
			$image.attr("src", tutorial.image);
			$("#image-source").attr("href", tutorial.image_source);
		}
		else
			console.log("[geotagx::tutorial::start::setTutorial] Error! Could not set image to analyze!");

		assertions_ = tutorial.assertions;
	}
	/**
	 * Returns the next question that has not been explicitly omitted.
	 */
	function getNextUnskippedQuestion(question, answer){
		var nextQuestion = getNextQuestion_(question, answer);
		var assertion = assertions_[nextQuestion];
		while (assertion && assertion.skip){
			nextQuestion = getNextQuestion_(nextQuestion, "Unknown");
			assertion = assertions_[nextQuestion];
		}
		return nextQuestion;
	}
	/**
	 * A user-defined method that displays the next question. This method
	 * prevents the questionnaire from automatically progressing to the next
	 * question. Instead, it validates the user's answer and if it matches with
	 * an expected expected, a notification containing a 'NEXT' button is
	 * displayed, thereby allowing the user to advance to the next question.
	 * If the answer does not match, a different kind of notification -- inviting
	 * the user to try again -- is displayed.
	 */
	function onShowNextQuestion(question, answer, $submitter){
		var assertion = assertions_[question];
		var message = assertion.default_message;
		var isExpectedAnswer = false;
		if ($.type(answer) === "string"){
			isExpectedAnswer = answer.toLowerCase() === assertion.expects.toLowerCase();

			var m = assertion.messages;
			message = m[answer] || m[answer.toLowerCase()] || m[answer.toUpperCase()] || message;
		}
		else
			isExpectedAnswer = answer === assertion.expects;

		if (isExpectedAnswer){
			nextQuestion_ = getNextUnskippedQuestion(question, answer);
			geotagx.analytics.onCorrectTutorialAnswer();
		}
		else
			geotagx.analytics.onWrongTutorialAnswer();

		showNotification(message, isExpectedAnswer);
	}
	/**
	 * A method that is called when a new question is presented to the user.
	 */
	function onQuestionChanged(question){
		var assertion = assertions_[question];
		if (assertion){
			var autoComplete = assertion.autocomplete;
			if (autoComplete){
				// The analytic's questionId parameter needs to be updated manually.
				geotagx.analytics.onQuestionChanged(question);

				var selector = ".question[data-id='" + question + "'] .answer ";
				// When auto-complete is set to true, we need to fill the
				// input with the expected answer and trigger the 'Done' button.
				var $input = $(selector + "input");
				if ($input.length > 0){
					$input.val(assertion.expects);
					$input.prop("disabled", true);
					var $button = $(".question[data-id='" + question + "'] .answer button.btn-answer[value='Done']");
					if ($button.length > 0)
						$button.trigger("click");
				}
			}
		}
	}

	function showNotification(message, isExpected){
		var $box = $("#tutorial-message-box");

		$box.removeClass("hide").hide();
		if (isExpected){
			$box.addClass("expected");
			$("#tutorial-success-message").html(message);
		}
		else {
			$box.removeClass("expected");
			$("#tutorial-failure-message").html(message);
		}
		$box.fadeIn(250);
	}

	function hideNotification(onNotificationHidden){
		$("#tutorial-message-box").fadeOut(150, function(){
			$(this).addClass("hide");

			if (onNotificationHidden && $.type(onNotificationHidden) === "function")
				onNotificationHidden();
		})
	}

	// Expose the API.
	geotagx.tutorial = api_;
})(window.geotagx = window.geotagx || {}, jQuery);
