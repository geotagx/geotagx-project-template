/*
 * The GeoTag-X project helper.
 */
;(function(geotagx, $, undefined){
	"use strict";

	var api_ = {}; // The project API.
	var shortName_; // The project's short name.

	/**
	 * Begins the project.
	 * @param shortName the project's short name.
	 * @param getNextQuestion a user-defined function that returns the id of the next question to present to the user.
	 */
	api_.start = function(shortName, getNextQuestion, isTutorial, tutorial){
		if ($.type(shortName) !== "string"){
			console.log("[geotagx::project::start] Error! Invalid project slug.");
			return;
		}
		shortName_ = shortName;

		if (isTutorial)
			geotagx.tutorial.start(shortName, getNextQuestion, tutorial);
		else {
			geotagx.questionnaire.onGetNextQuestion(getNextQuestion);

			pybossa.taskLoaded(onTaskLoaded);
			pybossa.presentTask(onTaskPresented);
			pybossa.run(shortName_);
		}

		geotagx.analytics.onProjectChanged(shortName_);
	};
	/**
	 * Returns the project's short name.
	 */
	api_.getShortName = function(){
		return shortName_;
	};
	/**
	 * Handles PyBossa's taskLoaded event.
	 */
	function onTaskLoaded(task, deferred){
		if (!$.isEmptyObject(task))
			$("<img/>").load(function(){ deferred.resolve(task); }).attr("src", task.info.image_url);
		else
			deferred.resolve(task);
	}
	/**
	 * Handles PyBossa's presentTask event.
	 */
	function onTaskPresented(task, deferred){
		if (!$.isEmptyObject(task)){
			// Show/hide respective elements.
			$(".show-on-task-loaded").removeClass("show-on-task-loaded").hide().fadeIn(200);
			$(".hide-on-task-loaded").hide();

			// Initialize the image to analyze.
			var $image = $("#image");
			if ($image.length > 0){
				$image.attr("src", task.info.image_url);

				$("#image-source").attr("href", task.info.source_uri);
			}
			else
				console.log("[geotagx::project::onTaskPresented] Error! Could not find image to analyze.");

			// Set the submission button's handler. Note that off().on() removes the previous handler
			// and sets a new one, every time a new task is loaded. This prevents a chain of events
			// being called when a button is pushed once.
			$("#questionnaire-submit").off("click.task").on("click.task", function(){
				var $button = $(this);
				$button.prop("disabled", true);

				// Append the image URL to the questionnaire results.
				var taskRun_ = geotagx.questionnaire.getAnswers();
				taskRun_.img = task.info.image_url;

				pybossa.saveTask(task.id, taskRun_).done(function(){
					geotagx.questionnaire.showFullSummary(false);

					$button.prop("disabled", false);
					deferred.resolve();
				});
			});

			geotagx.analytics.onTaskChanged(task.id);
			geotagx.questionnaire.start(1);
		}
	}
	// Expose the API.
	geotagx.project = api_;
})(window.geotagx = window.geotagx || {}, jQuery);
