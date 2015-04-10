// Run the application.
geotagx.task.run("geotagx_project_template_aksjdh", function(question, answer, $submitter){
    geotagx.task.saveAnswer(answer); 
    switch (question){
        case 8: //Final Question
            geotagx.task.finish();
            break;
        case 3:
            if(answer=="No"){
                geotagx.task.showQuestion(6);
            }
            break;
        default:
            geotagx.task.showNextQuestion();
            break;
    }
});
