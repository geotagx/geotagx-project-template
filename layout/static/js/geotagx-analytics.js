/*
 * The GeoTag-X project analytics tracker.
 */
;(function(geotagx, $, undefined){
	"use strict";

	var api_ = {}; // The analytics API.
	var projectId_ = 0; // The current project's identifier, i.e. its short_name.
	var taskId_ = 0; // The current task's identifier.
	var questionId_ = 0; // The current question identifier.

	$(document).ready(function(){
		// $(".external-link").on("click.analytics", onClickedExternalLink);
		// $(".social-media-link").on("click.analytics", onSharedProject);

		$(".skeleton.wet-run .btn-answer").on("click.analytics", onAnswerSubmitted);

		//FIXME Image scrolling (zooming) events aren't generated...
		$(".skeleton.dry-run #image").on("zoom.analytics", onTutorialImageZoom);
		$(".skeleton.wet-run #image").on("zoom.analytics", onImageZoom);

		$(".skeleton.dry-run #image-source").on("click.analytics", onShowTutorialImageSource);
		$(".skeleton.wet-run #image-source").on("click.analytics", onShowImageSource);

		$(".skeleton.dry-run #questionnaire-rewind").on("click.analytics", onShowPreviousTutorialQuestion);
		$(".skeleton.wet-run #questionnaire-rewind").on("click.analytics", onShowPreviousQuestion);

		$(".skeleton.dry-run #questionnaire-show-comments").on("click.analytics", onShowTutorialComments);
		$(".skeleton.wet-run #questionnaire-show-comments").on("click.analytics", onShowComments);

		$(".skeleton.dry-run .help-toggle").on("click.analytics", onShowTutorialHelp);
		$(".skeleton.wet-run .help-toggle").on("click.analytics", onShowHelp);
	});
	/**
	 * Starts tracking analytics for the project with the specified identifier.
	 */
	api_.start = function(projectId){
		projectId_ = projectId;
		console.log("analytics.action.startProject(" + projectId_ + ", " + window.location.href + ")");
	}
	/**
	 * Updates the tracking parameters when a new task is presented to the user.
	 */
	api_.onTaskChanged = function(taskId){
		taskId_ = taskId;
	}
	/**
	 * Updates the tracking parameters when a new question is presented to the user.
	 */
	api_.onQuestionChanged = function(questionId){
		questionId_ = questionId;
	}

	api_.onCorrectTutorialAnswer = function(){
		console.log("analytics.action.answerCorrect(" + projectId_ + ", " + questionId_ + ")");
	};

	api_.onWrongTutorialAnswer = function(){
		console.log("analytics.action.answerIncorrect(" + projectId_ + ", " + questionId_ + ")");
	};

	function onAnswerSubmitted(){
		console.log($(this).val());
		console.log("analytics.action.answerProject(" + projectId_ + ", " + taskId_ + ", " + questionId_ + ")");
	}

	function onTutorialImageZoom(){
		console.log("analytics.action.photoZoomTut(" + projectId_ + ", " + questionId_ + ")");
	}

	function onImageZoom(){
		console.log("analytics.action.photoZoom(" + projectId_ + ", " + taskId_ + ", " + questionId_ + ")");
	}

	function onShowTutorialImageSource(){
		console.log("analytics.action.viewPhotoSourceTut(" + projectId_ + ", " + questionId_ + ")");
	}

	function onShowImageSource(){
		console.log("analytics.action.viewPhotoSource(" + projectId_ + ", " + taskId_ + ", " + questionId_ + ")");
	}

	function onShowPreviousTutorialQuestion(){
		console.log("analytics.action.previousQuestionTut(" + projectId_ + ", " + questionId_ + ")");
	}

	function onShowPreviousQuestion(){
		console.log("analytics.action.previousQuestion(" + projectId_ + ", " + taskId_ + ", " + questionId_ + ")");
	}

	function onShowTutorialComments(){
		console.log("analytics.action.showCommentsTut(" + projectId_ + ", " + questionId_ + ")");
	}

	function onShowComments(){
		console.log("analytics.action.showComments(" + projectId_ + ", " + taskId_ + ", " + questionId_ + ")");
	}

	function onShowTutorialHelp(){
		console.log("analytics.action.helpRequest(" + projectId_ + ", " + questionId_ + ")");
	}

	function onShowHelp(){
		console.log("analytics.action.helpRequest(" + projectId_ + ", " + taskId_ + ", " + questionId_ + ")");
	}

	// Expose the API.
	geotagx.analytics = api_;
})(window.geotagx = window.geotagx || {}, jQuery);
