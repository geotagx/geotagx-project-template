/*
 * The GeoTag-X OpenLayers wrapper.
 */
;(function(geotagx, $, undefined){
	"use strict";

	/**
	 * Creates a Map object which includes a private internal map (an actual OpenLayers map)
	 * object and an accessor to the aforementioned object.
	 */
	var Map = function(targetId){
		this.openLayersMap_ = createOpenLayersMap(targetId);
	};
	/**
	 * Removes any plotted polygons or selected countries from the map.
	 * If center is set to true, the map is centered at the origin.
	 */
	Map.prototype.reset = function(center){
		if (this.openLayersMap_){
			var vectorLayer = getVectorLayer(this.openLayersMap_);
			if (vectorLayer)
				vectorLayer.getSource().clear();

			if (center){
				var view = this.openLayersMap_.getView();
				if (view){
					view.setCenter([0, 0]);
					view.setZoom(1);
				}
			}
		}
	}
	/**
	 * Centers the map at the specified location.
	 * If the input element is specified, then its value will be updated with the location's full name.
	 */
	Map.prototype.setLocation = function(location, input){
		if (location && typeof(location) === "string"){
			var map = this.openLayersMap_;
			if (map){
				// Query OpenStreetMap for the location's coordinates.
				$.getJSON("http://nominatim.openstreetmap.org/search/" + location + "?format=json&limit=1", function(results){
					if (results.length > 0){
						var result = results[0];
						var latitude = parseFloat(result.lat);
						var longitude = parseFloat(result.lon);
						var center = ol.proj.transform([longitude, latitude], "EPSG:4326", "EPSG:3857");

						var view = map.getView();
						view.setCenter(center);
						view.setZoom(8);

						// If an input field was specified, replace its value with the location's full name.
						if (input)
							input.value = result.display_name;
					}
					else
						console.log("Location not found."); // e.g. xyxyxyxyxyxyx
				});
			}
		}
	};
	/**
	 * Returns an object that contains all selected country names and regions (polygons).
	 */
	Map.prototype.getSelectedCountries = function(){
		var features = null;
		if (this.openLayersMap_){
			var interactions = this.openLayersMap_.getInteractions();

			// The select interaction was the last to be inserted and is therefore the last item in the collection.
			var selectInteraction = interactions.item(interactions.getLength() - 1);
			features = selectInteraction.getFeatures();
		}
		return new SelectedCountries(features);
	};
	/**
	 *
	 */
	var SelectedCountries = function(features){
		this.selection_ = {};
		if (features){
			features.forEach(function(feature, i){
				var name = feature.get("name");
				var polygon = feature.getGeometry().getCoordinates()[0];
				this.selection_[name] = polygon;
			}, this);
		}
	};
	/**
	 * Returns the set of names of the selected countries.
	 */
	SelectedCountries.prototype.getNames = function(){
		return Object.keys(this.selection_);
	};
	/**
	 * Returns the set of polygons the define the region of the selected countries.
	 */
	SelectedCountries.prototype.getPolygons = function(){
		var polygons = [];
		for (var name in this.selection_)
			polygons.push(this.selection_[name]);

		return polygons;
	};
	/**
	 * Creates an OpenLayers map instance in the DOM element with the specified ID.
	 */
	function createOpenLayersMap(targetId){
		// Create the map iff the DOM element exists.
		if (!document.getElementById(targetId))
			return null;

		var tileLayer = new ol.layer.Tile({
			source:new ol.source.MapQuest({layer:"osm"})
		});

		var vectorLayer = new ol.layer.Vector({
			source:new ol.source.Vector({
				url:"http://openlayers.org/en/v3.6.0/examples/data/geojson/countries.geojson",
				//url:"data/countries.geojson",
				format:new ol.format.GeoJSON()
			}),
			style: new ol.style.Style({
				stroke:new ol.style.Stroke({
					color:"#FFCC33"
				})
			})
		});

		// Create an interaction that allows us to select a predefined region on the map.
		var selectInteraction = new ol.interaction.Select();

		return new ol.Map({
			target:targetId,
			layers:[tileLayer, vectorLayer],
			interactions:ol.interaction.defaults().extend([selectInteraction]), // Important: Update Map.getSelectedCountries if you change this field.
			view:new ol.View({center:[0, 0], zoom:4})
		});
	}
	/**
	 * Returns the specified map's tile layer.
	 * Note that this function assumes that the tile layer is stored as the first in the map's layers collection.
	 */
	function getTileLayer(map){
		var tile = null;
		if (map){
			var layers = map.getLayers();
			tile = layers.getLength() > 0
			     ? layers.item(0)
			     : null;
		}
		return tile;
	}
	/**
	 * Returns the specified map's vector layer.
	 * Note that this function assumes that the vector layer is stored as the second in the map's layers collection.
	 */
	function getVectorLayer(map){
		var vector = null;
		if (map){
			var layers = map.getLayers();
			vector = layers.getLength() > 1
			       ? layers.item(1)
			       : null;
		}
		return vector;
	}

	// Expose the wrapper API.
	geotagx.ol = {
		/**
		 * Creates an instance of the OpenLayers map.
		 */
		createMap:function(targetId){
			return new Map(targetId);
		}
	};
})(window.geotagx = window.geotagx || {}, jQuery);
