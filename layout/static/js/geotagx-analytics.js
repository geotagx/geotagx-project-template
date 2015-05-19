/*
 * The GeoTag-X project analytics tracker.
 */
;(function(geotagx, $, undefined){
	"use strict";

	var api_ = {}; // The analytics API.
	var taskId_ = 0; // The current task's identifier.

	$(document).ready(function(){
		window.analyticsListener = true; // Enable the CCL analytics tracker library.

		// $(".external-link").on("click.analytics", onClickedExternalLink);
		// $(".social-media-link").on("click.analytics", onSharedProject);

		$("#project-task-presenter.analysis .btn-answer").on("click.analytics", onAnswerQuestion);

		//FIXME Image scrolling (zooming) events aren't generated...
		$("#project-task-presenter.tutorial #image").on("zoom.analytics", onTutorialImageZoom);
		$("#project-task-presenter.analysis #image").on("zoom.analytics", onImageZoom);

		$("#project-task-presenter.tutorial #image-source").on("click.analytics", onShowTutorialImageSource);
		$("#project-task-presenter.analysis #image-source").on("click.analytics", onShowImageSource);

		$("#project-task-presenter.tutorial #questionnaire-rewind").on("click.analytics", onShowPreviousTutorialQuestion);
		$("#project-task-presenter.analysis #questionnaire-rewind").on("click.analytics", onShowPreviousQuestion);

		$("#project-task-presenter.tutorial #questionnaire-show-comments").on("click.analytics", onShowTutorialComments);
		$("#project-task-presenter.analysis #questionnaire-show-comments").on("click.analytics", onShowComments);

		$("#project-task-presenter.tutorial .help-toggle").on("click.analytics", onShowTutorialHelp);
		$("#project-task-presenter.analysis .help-toggle").on("click.analytics", onShowHelp);
	});
	/**
	 * Starts tracking analytics for the project with the specified identifier,
	 * and the user with the given identifier.
	 * @param projectId the project's identifier, i.e. its short_name.
	 * @param userId the current user's identifier, which is either a username, or an IP address for anonymous users.
	 */
	api_.start = function(projectId, userId){
		analytics.setGlobal("userId", userId ? userId : "anonymous");
		analytics.setGlobal("projectId", projectId);
		analytics.fireEvent("action.startProject", {"url":window.location.href});
	}
	/**
	 * Updates the tracking parameters when a new task is presented to the user.
	 * @param taskId the task's identifier.
	 */
	api_.onTaskChanged = function(taskId){
		taskId_ = taskId;
	}
	/**
	 * Updates the tracking parameters when a new question is presented to the user.
	 * @param questionId the current question identifier.
	 */
	api_.onQuestionChanged = function(questionId){
		analytics.setGlobal("questionId", questionId);
	}
	/**
	 * Fires an event when a user selects the correct answer in a tutorial.
	 */
	api_.onCorrectTutorialAnswer = function(){
		analytics.fireEvent("action.correctTutorialAnswer");
	};
	/**
	 * Fires an event when a user selects the wrong answer in a tutorial.
	 */
	api_.onWrongTutorialAnswer = function(){
		analytics.fireEvent("action.wrongTutorialAnswer");
	};
	/**
	 * Fires an event when a user answers a question during an analysis.
	 */
	function onAnswerQuestion(){
		analytics.fireEvent("action.answerQuestion", {"taskId":taskId_, "buttonValue":$(this).val()});
	}
	/**
	 * Fires an event when a user zooms in on an image during a tutorial.
	 */
	function onTutorialImageZoom(){
		analytics.fireEvent("action.tutorialImageZoom");
	}
	/**
	 * Fires an event when a user zooms in on an image during an analysis.
	 */
	function onImageZoom(){
		analytics.fireEvent("action.imageZoom", {"taskId":taskId_});
	}
	/**
	 * Fires an event when a user visits an image's source during a tutorial.
	 */
	function onShowTutorialImageSource(){
		analytics.fireEvent("action.showTutorialImageSource");
	}
	/**
	 * Fires an event when a user visits an image's source during an analysis.
	 */
	function onShowImageSource(){
		analytics.fireEvent("action.showImageSource", {"taskId":taskId_});
	}
	/**
	 * Fires an event when a user goes back to a previous question during a tutorial.
	 */
	function onShowPreviousTutorialQuestion(){
		analytics.fireEvent("action.showPreviousTutorialQuestion");
	}
	/**
	 * Fires an event when a user goes back to a previous question during an analysis.
	 */
	function onShowPreviousQuestion(){
		analytics.fireEvent("action.showPreviousQuestion", {"taskId":taskId_});
	}
	/**
	 * Fires an event when a user clicks the 'Show Comments' button during a tutorial.
	 */
	function onShowTutorialComments(){
		analytics.fireEvent("action.showTutorialComments");
	}
	/**
	 * Fires an event when a user clicks the 'Show Comments' button during an analysis.
	 */
	function onShowComments(){
		analytics.fireEvent("action.showComments", {"taskId":taskId_});
	}
	/**
	 * Fires an event when a user clicks a question's help toggle during a tutorial.
	 */
	function onShowTutorialHelp(){
		analytics.fireEvent("action.showTutorialHelp");
	}
	/**
	 * Fires an event when a user clicks a question's help toggle during an analysis.
	 */
	function onShowHelp(){
		analytics.fireEvent("action.showHelp", {"taskId":taskId_});
	}

	// Expose the API.
	geotagx.analytics = api_;
})(window.geotagx = window.geotagx || {}, jQuery);
