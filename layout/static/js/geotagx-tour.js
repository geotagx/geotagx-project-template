/*
 * The GeoTag-X tour helper.
 */
;(function(geotagx, $, undefined){
	"use strict";

	var api_ = {}; // The tour API.
	var questionnaireTour_ = null;

	/**
	 * Returns true if the questionnaire tour ended, false otherwise.
	 */
	api_.questionnaireTourEnded = function(){
		return questionnaireTour_ && questionnaireTour_.ended();
	};
	/**
	 * Starts a questionnaire tour.
	 * @param force forces the tour start, even if it was already completed.
	 */
	api_.startQuestionnaireTour = function(force){
		// Only start the tour if it hasn't already been taken.
		var questionnaireTourTaken = /*!force &&*/ api_.questionnaireTourEnded();
		if (!questionnaireTourTaken){
			localStorage.setItem("geotagx_questionnaire_tour_current_step", 0);

			if (!questionnaireTour_){
				questionnaireTour_ = new Tour({
					name:"geotagx_questionnaire_tour",
					orphan:true,
					steps:[
						{
							orphan:true,
							title:"Welcome!",
							content:"It seems as though you are new around here. How about we take a tour?<br><small>Note: You can navigate faster by using the left (&#8592;) and right (&#8594;) arrow keys.</small>"
						},
						{
							element: "#questionnaire-summary",
							placement:"bottom",
							title:"The Summary",
							content:"This section provides feedback while you progress through the questionnaire."
						},
						{
							element: "#image-section",
							placement:"top",
							title:"The Image",
							content:"You will be tasked with analysing an image. When you complete an analysis, a new image will be presented to you."
						},
						{
							element: "#questionnaire-question-1 > .title",
							placement:"bottom",
							title:"The Question",
							content:"This is one of many questions asked about the image to the right. Try to answer it to the best of your capabilities ..."
						},
						{
							element: "#questionnaire-question-1 .help-toggle",
							placement:"bottom",
							title:"Help!",
							content:"... but remember, if you are having trouble answering a question, take a look at the help ..."
						},
						{
							element: "#image-source",
							placement:"bottom",
							title:"Image source",
							content:"... and the image source. More often than not, the source will give you a context as well as additional information that may prove to be invaluable."
						}
					]
				});
				questionnaireTour_.init();
			}
			questionnaireTour_.start(true);
		}
	};

	// Expose the API.
	geotagx.tour = api_;
})(window.geotagx = window.geotagx || {}, jQuery);
