/* Define a custom script for your project here. */

// Run the application.
geotagx.task.run(window.geotagx_project_short_name, function(question, answer){
    geotagx.task.showNextQuestion();
});
