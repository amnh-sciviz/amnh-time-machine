'use strict';

var App = (function() {

  function App(config) {
    var defaults = {
      "dataUrl": "data/ui.json",
      "startYear": 1935,
      "maxItems": 18,
      "maxExpeditions": 20
    };
    this.opt = _.extend({}, defaults, config);
    this.init();
  }

  function loadData(url){
    var deferred = $.Deferred();
    $.getJSON(url, function(data) {
      console.log("Loaded data.");
      deferred.resolve(data);
    });
    return deferred.promise();
  }

  function norm(value, a, b){
    var denom = (b - a);
    if (denom > 0 || denom < 0) {
      return (1.0 * value - a) / denom;
    } else {
      return 0;
    }
  }

  function preloadImages(images){
    _.each(images, function(src){
      var img =  new Image();
      img.src = src;
    });
  }

  App.prototype.init = function(){
    var _this = this;

    this.$logo = $("#logo");
    this.$report = $("#report");
    this.$items = $("#items");
    this.$expeditions = $("#expeditions");
    this.$floorplans = $("#floor-plan");
    this.$map = $("#expedition-map-labels");
    this.$events = $("#events");
    this.$eventsContainer = this.$events.parent();

    this.selectedFloor = 1;

    var dataPromise = loadData(this.opt.dataUrl);
    $.when(dataPromise).done(function(results){
      _this.onDataLoad(results)
    });
  };

  App.prototype.changeFloor = function(floor){
    floor = parseInt(floor);
    $(".floor").removeClass("selected");
    $('.floor[data-floor="'+floor+'"]').addClass("selected");
    this.selectedFloor = floor;
  };

  App.prototype.loadUI = function(){
    var _this = this;
    var data = this.data;

    // preload images
    preloadImages(_.pluck(data.reports, 'image'));
    preloadImages(_.pluck(data.floorPlans, 'image'));
    preloadImages(_.pluck(data.logos, 'image'));

    // load slider
    var $handleText = $("#handle-text");
    $("#slider").slider({
      min: _this.yearStart,
      max: _this.yearEnd,
      value: _this.opt.startYear,
      create: function() {
        var value = $(this).slider("value");
        $handleText.text(value);
        _this.onSlide(value);
      },
      slide: function( event, ui ) {
        $handleText.text(ui.value);
        _this.onSlide(ui.value);
      }
    });

    // load floor links
    $(".floor-link").on("click", function(e){
      _this.changeFloor($(this).attr("data-floor"))
    });

    $(".rotate-link").on("click", function(e){
      _this.rotateFloorPlan($(this).hasClass("rotated"));
    });

  };

  App.prototype.onDataLoad = function(data){
    this.data = data;
    this.yearStart = data.yearStart;
    this.yearEnd = data.yearEnd;
    this.years = data.years;
    this.dataKeys = data.dataKeys;

    this.loadUI();

  };

  App.prototype.onSlide = function(year){
    var _this = this;
    var yearIndex = year - this.yearStart;
    var yearData = this.years[yearIndex];

    _.each(this.dataKeys, function(key, i){
      var data = yearData[i];
      if (key==="logos") _this.renderLogo(data);
      else if (key==="floorPlans") _this.renderFloorplans(data);
      else if (key==="reports") _this.renderReports(data);
      else if (key==="items") _this.renderItems(data);
      else if (key==="expeditions") _this.renderExpeditions(data);
      else if (key==="events") _this.renderEvents(data);
    });
  };

  App.prototype.renderEvents = function(data){
    var items = [];
    var itemData = this.data.events;
    _.each(data, function(index){
      items.push(itemData[index]);
    });

    // if (items.length) this.$eventsContainer.addClass("active");
    // else this.$eventsContainer.removeClass("active");

    if (!items.length) {
      this.$events.html($('<p>No events this year</p>'));
      return;
    }

    var $items = $("<div />");
    _.each(items, function(item){
      $items.append($('<p><a href="'+item.url+'">'+item.title+'</a></p>'));
    });
    this.$events.html($items);
  }

  App.prototype.renderExpeditions = function(data){
    if (data.length > this.opt.maxItems) {
      data = data.slice(0, this.opt.maxExpeditions);
    }

    var items = [];
    var itemData = this.data.expeditions;
    _.each(data, function(index){
      items.push(itemData[index]);
    });

    var $mapItems = $("<div />");
    _.each(items, function(item){
      if (isNaN(item.lon) || isNaN(item.lat)) return;

      var $mapItem = $('<a href="'+item.url+'" title="'+item.title+'" class="label"></a>');
      $mapItem.css({
        "left": (norm(item.lon, -180, 180) * 100) + "%",
        "top": (norm(item.lat, 90, -90) * 100) + "%"
      });
      $mapItems.append($mapItem);
    });
    this.$map.html($mapItems);

    var $items = $("<div />");
    _.each(items, function(item){
      var str = '<a href="'+item.url+'">';
      if (item.event.length) {
        str += item.event;
        str += '<small>'+item.title+'</small>';
      } else {
        str += item.title;
      }
      if (item.place.length) str += '<span class="place">'+item.place+'</span>'
      str += '</a>';
      $items.append($(str));
    });
    this.$expeditions.html($items);
  };

  App.prototype.renderFloorplans = function(data){
    if (!data.length) return false;

    var items = [];
    var itemData = this.data.floorPlans;
    _.each(data, function(index){
      items.push(itemData[index]);
    });
    items = _.sortBy(items, function(item){ return item.floor; });

    var selectedFloor = this.selectedFloor;
    var $items = $("<div />");
    _.each(items, function(item, i){
      var selected = item.floor === selectedFloor ? "selected" : "";
      $items.append($('<img src="'+item.image+'" class="'+selected+' floor" data-floor="'+(i+1)+'" title="'+item.year+' Floor plan '+(i+1)+'" alt="'+item.year+' Floor plan '+(i+1)+'" />'))
    });
    this.$floorplans.html($items);
  };

  App.prototype.renderItems = function(data){
    if (data.length > this.opt.maxItems) {
      data = data.slice(0, this.opt.maxItems);
    }

    var items = [];
    var itemData = this.data.items;
    _.each(data, function(index){
      items.push(itemData[index]);
    });

    var $items = $("<div />");
    _.each(items, function(item){
      $items.append($('<a href="'+item.url+'"><img src="'+item.image+'" alt="'+item.title+'" title="'+item.title+'" /></a>'))
    });
    this.$items.html($items);
  };

  App.prototype.renderLogo = function(data){
    if (!data.length) return false;
    var index = data[0];
    var logo = this.data.logos[index]

    this.$logo.attr("src", logo.image);
  };

  App.prototype.renderReports = function(data){
    if (!data.length) return false;
    var index = data[0];
    var report = this.data.reports[index];

    var $report = $("<div />");
    $report.append('<a href="'+report.url+'"><img src="'+report.image+'" alt="'+report.title+'" />'+report.title+'</a>');
    this.$report.html($report);
  };

  App.prototype.rotateFloorPlan = function(rotated){
    var $link = $(".rotate-link");
    if (rotated) {
      $(".rotate-link, .floor-plan").removeClass("rotated");
    } else {
      $(".rotate-link, .floor-plan").addClass("rotated");
    }
  };

  return App;

})();

$(function() {
  var app = new App({});
});
