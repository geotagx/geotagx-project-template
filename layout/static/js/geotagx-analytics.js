/*
 * The GeoTag-X project analytics tracker.
 */
(function(geotagx, $, undefined){
	"use strict";

	var projectId_ = 0; // The current project's identifier, i.e. its short_name.
	var taskId_ = 0; // The current task's identifier.
	var questionId_ = 0; // The current question identifier.
	var api_ = {}; // The analytics API.

	$(document).ready(function(){
		// $(".external-link").on("click.analytics", onClickedExternalLink);
		// $(".social-media-link").on("click.analytics", onSharedProject);

		$(".btn-answer").on("click.analytics", onSubmitAnswer);

		$("#image").on("scroll.analytics", onImageZoom); //FIXME Scrolling events aren't captured by the event handler.
		$("#image-source").on("click.analytics", onShowImageSource);
		$("#questionnaire-rewind").on("click.analytics", onShowPreviousQuestion);
		$("#questionnaire-show-comments").on("click.analytics", onShowComments);

		$(".help-toggle").on("click.analytics", onHelpRequested);
	});
	/**
	 * Starts tracking analytics for the project with the specified identifier.
	 */
	api_.start = function(projectId){
		projectId_ = projectId;
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





	function onSubmitAnswer(){
		console.log("Answer submitted.");
	}

	function onImageZoom(){
		console.log("Image zoomed.");
	}

	function onShowImageSource(){
		console.log("Image source clicked.");
	}

	function onShowPreviousQuestion(){
		console.log("Showing previous question.");
	}

	function onShowComments(){
		console.log("Comment visibility toggled.");
	}

	function onHelpRequested(){
		console.log("Help visibility toggled.");
	}

	// Expose the API.
	geotagx.analytics = api_;
})(window.geotagx = window.geotagx || {}, jQuery);
