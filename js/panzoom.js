'use strict';

var PanZoom = (function() {

  function PanZoom(config) {
    var defaults = {
      tileSources: "data/eac_relations.dzi",
      prefixUrl: "img/openseadragon/"
    };
    this.opt = $.extend({}, defaults, config);
    this.init();
  }

  PanZoom.prototype.init = function(){
    var opt = this.opt;
    var viewer = OpenSeadragon({
        id: "panzoom",
        prefixUrl: opt.prefixUrl,
        tileSources: opt.tileSources
    });
  };

  return PanZoom;

})();

$(function() {
  var app = new PanZoom({});
});
