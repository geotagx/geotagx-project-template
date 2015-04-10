// Run the application.
geotagx.task.run("yamuna_waters", function(question, answer, $submitter){
    switch (question){
        case 1: // Can you see any water in the photo?
        case 7: // Can you see any sources of drinking water?
            geotagx.task.saveAnswer(answer);
            if (answer === "Yes")
                geotagx.task.showNextQuestion();
            else
                geotagx.task.finish();
            break;
        case 2: // Can you see small pools of water?
            geotagx.task.saveAnswer(answer);
            geotagx.task.showQuestion(answer === "Yes" ? 3 : 4);
            break;
        case 3: // Are these small pools of water near human shelters or a settlement?
            geotagx.task.saveAnswer(answer);
            geotagx.task.showQuestion(7);
            break;
        case 4: // Can you see a large body of water?
            geotagx.task.saveAnswer(answer);
            geotagx.task.showQuestion(answer === "Yes" ? 5 : 6);
            break;
        case 5: // Can you see any signs of fast moving water?
        case 6: // Can you see any of the following flood protection measures?
        case 8: // Which sources of drinking water can you see?
            geotagx.task.saveAnswer(answer === "Done" ? $submitter.siblings("input:checked") : answer);
            geotagx.task.showNextQuestion();
            break;
        case 9: // Have they been affected by the flood waters?
        default:
            geotagx.task.saveAnswer(answer);
            geotagx.task.showNextQuestion();
            break;
    }
});
