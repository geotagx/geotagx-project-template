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

			// Update the user progress.
			pybossa.userProgress(shortName_).done(function(data){
				$("#project-task-count").text(data.done + "/" + data.total);
			});

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
			$("#submit-analysis").off("click.task").on("click.task", function(){
				var $busyIcon = $("#questionnaire-busy-icon");

				// Disable the submit button and display the busy icon.
				$busyIcon.removeClass("hide").hide().fadeIn(300);

				var $submitButton = $(this);
				$submitButton.toggleClass("busy btn-success");
				$submitButton.prop("disabled", true);

				// Append the image URL to the questionnaire results.
				var taskRun_ = geotagx.questionnaire.getAnswers();
				taskRun_.img = task.info.image_url;

				pybossa.saveTask(task.id, taskRun_).done(function(){
					$busyIcon.fadeOut(300, function(){ $(this).addClass("hide"); });

					// Display the status message.
					var $message = $("#submit-message-success");
					$message.removeClass("hide");
					setTimeout(function(){
						deferred.resolve();
						$message.addClass("hide");
						$submitButton.toggleClass("busy btn-success");
						$submitButton.prop("disabled", false);
					}, 1500);
				}).fail(function(response){
					$busyIcon.fadeOut(300, function(){ $(this).addClass("hide"); });
					$submitButton.toggleClass("busy btn-success");
					$submitButton.prop("disabled", false);

					var $message = $("#submit-message-failure");

					// If the status code is 403 (FORBIDDEN), then we assume that the
					// data was sent but the deferred object has not yet been resolved.
					if (response.status === 403){
						deferred.resolve();
						$message.addClass("hide");
					}
					else {
						console.log(response);

						$message.removeClass("hide");
						$submitButton.one("click", function(){
							$message.addClass("hide");
						});
					}
				});
			});
			geotagx.analytics.onTaskChanged(task.id);
			geotagx.questionnaire.start();
		}
		else {
			// If there're no more tasks, then hide the questionnaire and image,
			// then display the participation appreciation message.
			$("#participation-appreciation-section").removeClass("hide");
			$("#questionnaire-section").addClass("hide");
			$("#image-section").addClass("hide");
			$("#project-task-presenter-header").addClass("hide");
		}
	}
	// Expose the API.
	geotagx.project = api_;
})(window.geotagx = window.geotagx || {}, jQuery);
