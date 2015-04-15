// Run the application.
geotagx.task.run("{{slug}}", function(question, answer, $submitter){
    geotagx.task.saveAnswer(answer); 
    switch (question){
        case 6: //Final Question
            geotagx.task.finish();
            break;
        default:
            geotagx.task.showNextQuestion();
            break;
    }
});
