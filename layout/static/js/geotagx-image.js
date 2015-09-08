/*
 * The GeoTag-X Image helper.
 * The code is based heavily on Wheelzoom 3.0.2 by jacklmoore (http://www.jacklmoore.com/wheelzoom).
 *
 * Author: Jeremy Othieno.
 */
;(function(geotagx, $, undefined){
    "use strict";
    /**
     * Instantiate an Image object on the HTML element with the specified id.
     */
    var Image = function(id, options){
        this.frame = document.getElementById(id);
        this.frame.style.overflow = "hidden";
        this.frame.style.backgroundColor = "rgba(0, 0, 0, 0.25)";

        this.busyIcon = this.frame.appendChild(document.createElement("i"));
        this.busyIcon.className = "fa fa-3x fa-cog fa-spin";
        this.busyIcon.style.color = "#FFF";
        this.busyIcon.style.position = "absolute";
        this.busyIcon.style.display = "none";

        this.image = this.frame.appendChild(document.createElement("img"));
        this.image.style.width = "100%";
        this.image.addEventListener("wheel", onWheel.bind(this));
        this.image.addEventListener("mousedown", onMouseDown.bind(this));

        this.settings = $.extend({
            zoomFactor:0.15,
            discreetZoomFactor:0.45
        }, options);

        this.attributes = {
            x:0,   // The image's horizontal position.
            y:0,   // The image's vertical position.
            w:0,   // The image's width.
            h:0,   // The image's height.
            bgw:0, // The background width.
            bgh:0, // The background height.
            e:null // The previous event.
        };
    };
    /**
     * Returns the URL to the image.
     */
    Image.prototype.getSource = function(){
        return $(this.image).data("src");
    };
    /**
     * Sets the image source, i.e. the URL to the image.
     */
    Image.prototype.setSource = function(source){
        if ($.type(source) !== "string")
            return;

        var context = this;

        $(context.image).fadeOut(100, function(){
            if ($(context.image).data("src") == source){
                // If the new source is the same as the older one, there's no need to
                // change the image. Instead, we reset its zoom level.
                Image.prototype.zoomReset.call(context);
                $(context.image).fadeIn();
            }
            else {
                // Show the 'busy' icon.
                context.busyIcon.style.display = "block";

                // The 'src' attribute is overwritten by design, so we store a copy.
                $(context.image).attr("src", source).data("src", source);

                // Wait for the image to complete before we set it up.
                var interval = setInterval(function(){
                    if (context.image.complete){
                        clearInterval(interval);
                        context.busyIcon.style.display = "none";
                        $(context.image).fadeIn(0, function(){
                            context.frame.style.height = context.image.height + "px";
                            context.busyIcon.style.left = (($(context.frame).width() - $(context.busyIcon).width()) / 2) + "px";
                            context.busyIcon.style.top = (($(context.frame).height() - $(context.busyIcon).height()) / 2) + "px";
                            onLoaded(context.image, context.attributes);
                        });
                    }
                }, 300);
            }
        });
    };
    /**
     * Zoom in on the image.
     */
    Image.prototype.zoomIn = function(){
        // Zoom in on the center of the image.
        var x = this.image.width / 2;
        var y = this.image.height / 2;

        zoom(this, -1, this.settings.discreetZoomFactor, x, y);
    };
    /**
     * Zooms out of the image.
     */
    Image.prototype.zoomOut = function(){
        // Zoom out from the center of the image.
        var x = this.image.width / 2;
        var y = this.image.height / 2;

        zoom(this, 1, this.settings.discreetZoomFactor, x, y);
    };
    /**
     * Resets the image's zoom level.
     */
    Image.prototype.zoomReset = function(){
        this.attributes.x   = 0;
        this.attributes.y   = 0;
        this.attributes.bgw = this.attributes.w;
        this.attributes.bgh = this.attributes.h;

        updateImage(this.image, this.attributes);
    };
    /**
     * Rotates the image to the left.
     */
    Image.prototype.rotateLeft = function(){
    };
    /**
     * Rotates the image to the right.
     */
    Image.prototype.rotateRight = function(){
    };
    /**
     * A handler that is fired when the image is fully loaded.
     */
    function onLoaded(image, attributes){
        var computedStyle = window.getComputedStyle(image, null);

        attributes.w   = parseInt(computedStyle.width, 10);
        attributes.h   = parseInt(computedStyle.height, 10);
        attributes.bgw = attributes.w;
        attributes.bgh = attributes.h;
        attributes.x   = 0;
        attributes.y   = 0;

        image.style.backgroundImage = 'url("' + image.src + '")';
        image.style.backgroundRepeat = "no-repeat";
        image.style.backgroundSize = attributes.bgw + "px " + attributes.bgh + "px";
        image.style.backgroundPosition = "0 0";
        image.src = generateTransparentImage(image.naturalWidth, image.naturalHeight);
    }
    /**
     * Returns a transparent image with the specified width and height.
     */
    function generateTransparentImage(width, height){
        var canvas = document.createElement("canvas");
        canvas.width = width;
        canvas.height = height;

        return canvas.toDataURL();
    }
    /**
     * Updates the image.
     */
    function updateImage(image, attributes){
        if (attributes.x > 0)
            attributes.x = 0;
        else if (attributes.x < (attributes.w - attributes.bgw))
            attributes.x = attributes.w - attributes.bgw;

        if (attributes.y > 0)
            attributes.y = 0;
        else if (attributes.y < (attributes.h - attributes.bgh))
            attributes.y = attributes.h - attributes.bgh;

        image.style.backgroundSize = attributes.bgw + "px " + attributes.bgh + "px";
        image.style.backgroundPosition = attributes.x + "px " + attributes.y + "px";
    }
    /**
     * Zooms in/out of the image at the coordinates <x, y>.
     */
    function zoom(context, delta, factor, x, y){
        var attributes = context.attributes;

        // Record the offset between the bg edge and cursor:
        var bgCursorX = x - attributes.x;
        var bgCursorY = y - attributes.y;

        // Use the previous offset to get the percent offset between the bg edge and cursor:
        var bgRatioX = bgCursorX / attributes.bgw;
        var bgRatioY = bgCursorY / attributes.bgh;

        // Update the bg size:
        if (delta < 0){
            attributes.bgw += attributes.bgw * factor;
            attributes.bgh += attributes.bgh * factor;
        }
        else {
            attributes.bgw -= attributes.bgw * factor;
            attributes.bgh -= attributes.bgh * factor;
        }

        // Take the percent offset and apply it to the new size:
        attributes.x = x - (attributes.bgw * bgRatioX);
        attributes.y = y - (attributes.bgh * bgRatioY);

        // Prevent zooming out beyond the starting size
        if (attributes.bgw <= attributes.w || attributes.bgh <= attributes.h){
            attributes.x   = 0;
            attributes.y   = 0;
            attributes.bgw = attributes.w;
            attributes.bgh = attributes.h;
        }
        else
            $(image).trigger("zoom", delta < 0 ? -1 : 1);

        updateImage(context.image, attributes);
    }
    /**
     * A handler that is called when the user scrolls over the image.
     */
    function onWheel(e){
        e.preventDefault();

        var delta = e.deltaY ? e.deltaY : (e.wheelDelta ? -e.wheelDelta : 0);

        // As far as I know, there is no good cross-browser way to get the cursor position relative to the event target.
        // We have to calculate the target element's position relative to the document, and subtract that from the
        // cursor's position relative to the document.
        var rect = image.getBoundingClientRect();
        var x = e.pageX - rect.left - document.body.scrollLeft;
        var y = e.pageY - rect.top - document.body.scrollTop;

        zoom(this, delta, this.settings.zoomFactor, x, y);
    }
    /**
     * A handler that is called when the user clicks on an image.
     */
    function onMouseDown(e){
        e.preventDefault();

        var image = this.image;
        var attributes = this.attributes;

        attributes.e = e;

        document.addEventListener("mousemove", drag);
        document.addEventListener("mouseup", removeDrag);

        function drag(e){
            e.preventDefault();

            attributes.x += (e.pageX - attributes.e.pageX);
            attributes.y += (e.pageY - attributes.e.pageY);
            updateImage(image, attributes);

            attributes.e = e;
        }

        function removeDrag(){
            document.removeEventListener("mouseup", removeDrag);
            document.removeEventListener("mousemove", drag);
        }
    }

    geotagx.Image = Image;
})(window.geotagx = window.geotagx || {}, jQuery);
