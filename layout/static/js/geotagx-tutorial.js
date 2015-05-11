/*
 * The GeoTag-X tutorial helper.
 */
(function(geotagx, $, undefined){
	"use strict";

	var api_ = {}; // The tutorial API.
	var numberOfTutorials_ = 0; // The number of available tutorials.
	var currentTutorial_ = 0; // The index of the current tutorial.
	var assertions_ = null; // An object containing assertions about the image being analyzed.

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

		tutorial = [
			{
				"image":"http://i.imgur.com/yZrJpI3.jpg",
				"image_source":"http://imgur.com/r/earthporn/yZrJpI3",
				"assertions":{
					1:{
						expects:"no",
						default_message:"Try again. If you are not sure what to look for, check out the help for more information.",
						messages:{
							"no":"Well done! There is an animal in this photo.",
							"yes":"Try again. Are you sure there is no animal? Check out the help for information on what you should be looking for."
						}
					}
				}
			},
			{
				"image":"http://resources3.news.com.au/images/2013/05/24/1226650/215811-130525-luke-mcnevin.jpg",
				"image_source":"http://www.theaustralian.com.au/news/nation/spared-slaughter-overseas-only-to-meet-cruel-death-in-a-parched-land/story-e6frg6nf-1226650217008#",
				"assertions":{
					1:{
						expects:"yes",
						default_message:"Try again. If you are not sure what to look for, check out the help for more information.",
						messages:{
							"yes":"Well done! There is an animal in this photo.",
							"no":"Try again. Are you sure there is no animal? Check out the help for information on what you should be looking for."
						}
					}
				}
			}
		];

		numberOfTutorials_ = tutorial.length;
		currentTutorial_ = Math.floor((Math.random() * numberOfTutorials_)); // Select a random tutorial out of all available ones.
		setTutorial(tutorial[currentTutorial_]);

		// The next question's identifier. This value is determined each time
		// a correct answer is input by the user.
		var nextQuestion = 0;

		// Override the showNextQuestion function so that instead of automatically
		// displaying the next question, a notification is displayed to the user.
		// A notification may contain a "NEXT" button which allows a user to
		// advance to the next question.
		geotagx.questionnaire.onShowNextQuestion(function(question, answer, $submitter){
			answer = $.type(answer) === "string" ? answer.toLowerCase() : answer; // toLowerCase for case-insensitive comparisons.

			var assertion = assertions_[question];
			var message = assertion.messages[answer] ? assertion.messages[answer] : assertion.default_message;
			var isExpectedAnswer = answer === assertion.expects;
			if (isExpectedAnswer){
				nextQuestion = getNextQuestion(question, answer);
				geotagx.analytics.onCorrectTutorialAnswer();
			}
			else
				geotagx.analytics.onWrongTutorialAnswer();

			showNotification(message, isExpectedAnswer);
		});

		$(".show-on-task-loaded").removeClass("show-on-task-loaded").hide().fadeIn(200);
		$(".hide-on-task-loaded").hide();
		$("#tutorial-next-question").on("click.tutorial", function(){
			hideNotification();
			geotagx.questionnaire.showQuestion(nextQuestion);
		});
		$("#tutorial-another").on("click.tutorial", function(){
			currentTutorial_ = (currentTutorial_ + 1) % numberOfTutorials_;
			setTutorial(tutorial[currentTutorial_]);
			geotagx.questionnaire.showFullSummary(false);
			geotagx.questionnaire.start(1);
		});

		geotagx.questionnaire.start(1);
		geotagx.analytics.start(shortName);
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
		$box.fadeIn(300);
	}

	function hideNotification(){
		$("#tutorial-message-box").fadeOut(300, function(){
			$(this).addClass("hide");
		})
	}

	// Expose the API.
	geotagx.tutorial = api_;
})(window.geotagx = window.geotagx || {}, jQuery);
