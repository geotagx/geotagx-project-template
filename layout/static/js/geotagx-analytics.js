/*
 * The GeoTag-X project analytics tracker.
 */
;(function(geotagx, $, undefined){
	"use strict";

	var api_ = {}; // The project-specific analytics API.
	var taskId_ = 0; // The current task's identifier.
	var projectId_ = null; // The current project's short name.
	var questionId_ = 0; // The current question number.

	$(document).ready(function(){
		// If analytics is not enabled, do nothing.
		if (!window.analyticsListener)
			return;

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
	 * Updates the tracking parameters when a new project is started.
	 * @param projectId the project's short name.
	 */
	api_.onProjectChanged = function(projectId){
		projectId_ = projectId;
	};
	/**
	 * Updates the tracking parameters when a new task is presented to the user.
	 * @param taskId the task's identifier.
	 */
	api_.onTaskChanged = function(taskId){
		taskId_ = taskId;
	};
	/**
	 * Updates the tracking parameters when a new question is presented to the user.
	 * @param questionId the current question identifier.
	 */
	api_.onQuestionChanged = function(questionId){
		questionId_ = questionId;
	};
	/**
	 * Fires an event when a user selects the correct answer in a tutorial.
	 */
	api_.onCorrectTutorialAnswer = function(){
		var data = {
			"projectId":projectId_,
			"questionId":questionId_
		};
		analytics.fireEvent("action.correctTutorialAnswer", data);
	};
	/**
	 * Fires an event when a user selects the wrong answer in a tutorial.
	 */
	api_.onWrongTutorialAnswer = function(){
		var data = {
			"projectId":projectId_,
			"questionId":questionId_
		};
		analytics.fireEvent("action.wrongTutorialAnswer", data);
	};
	/**
	 * Fires an event when a user answers a question during an analysis.
	 */
	function onAnswerQuestion(){
		var data = {
			"projectId":projectId_,
			"questionId":questionId_,
			"taskId":taskId_,
			"buttonValue":$(this).val()
		};
		analytics.fireEvent("action.answerQuestion", data);
	}
	/**
	 * Fires an event when a user zooms in on an image during a tutorial.
	 */
	function onTutorialImageZoom(){
		var data = {
			"projectId":projectId_,
			"questionId":questionId_
		};
		analytics.fireEvent("action.tutorialImageZoom", data);
	}
	/**
	 * Fires an event when a user zooms in on an image during an analysis.
	 */
	function onImageZoom(){
		var data = {
			"projectId":projectId_,
			"questionId":questionId_,
			"taskId":taskId_
		};
		analytics.fireEvent("action.imageZoom", data);
	}
	/**
	 * Fires an event when a user visits an image's source during a tutorial.
	 */
	function onShowTutorialImageSource(){
		var data = {
			"projectId":projectId_,
			"questionId":questionId_
		};
		analytics.fireEvent("action.showTutorialImageSource", data);
	}
	/**
	 * Fires an event when a user visits an image's source during an analysis.
	 */
	function onShowImageSource(){
		var data = {
			"projectId":projectId_,
			"questionId":questionId_,
			"taskId":taskId_
		};
		analytics.fireEvent("action.showImageSource", data);
	}
	/**
	 * Fires an event when a user goes back to a previous question during a tutorial.
	 */
	function onShowPreviousTutorialQuestion(){
		var data = {
			"projectId":projectId_,
			"questionId":questionId_
		};
		analytics.fireEvent("action.showPreviousTutorialQuestion", data);
	}
	/**
	 * Fires an event when a user goes back to a previous question during an analysis.
	 */
	function onShowPreviousQuestion(){
		var data = {
			"projectId":projectId_,
			"questionId":questionId_,
			"taskId":taskId_
		};
		analytics.fireEvent("action.showPreviousQuestion", data);
	}
	/**
	 * Fires an event when a user clicks the 'Show Comments' button during a tutorial.
	 */
	function onShowTutorialComments(){
		var data = {
			"projectId":projectId_,
			"questionId":questionId_
		};
		analytics.fireEvent("action.showTutorialComments", data);
	}
	/**
	 * Fires an event when a user clicks the 'Show Comments' button during an analysis.
	 */
	function onShowComments(){
		var data = {
			"projectId":projectId_,
			"questionId":questionId_,
			"taskId":taskId_
		};
		analytics.fireEvent("action.showComments", data);
	}
	/**
	 * Fires an event when a user clicks a question's help toggle during a tutorial.
	 */
	function onShowTutorialHelp(){
		var data = {
			"projectId":projectId_,
			"questionId":questionId_
		};
		analytics.fireEvent("action.showTutorialHelp", data);
	}
	/**
	 * Fires an event when a user clicks a question's help toggle during an analysis.
	 */
	function onShowHelp(){
		var data = {
			"projectId":projectId_,
			"questionId":questionId_,
			"taskId":taskId_
		};
		analytics.fireEvent("action.showHelp", data);
	}

	// Expose the API.
	geotagx.analytics = api_;
})(window.geotagx = window.geotagx || {}, jQuery);
