'use strict';

var App = (function() {

  function App(config) {
    var defaults = {
      "dataUrl": "data/ui.json",
      "startYear": 2016,
      "maxItems": 9,
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

  App.prototype.init = function(){
    var _this = this;

    this.$logo = $("#logo");
    this.$report = $("#report");
    this.$items = $("#items");
    this.$expeditions = $("#expeditions");
    this.$floorplans = $("#floor-plan");

    this.selectedFloor = 1;

    var dataPromise = loadData(this.opt.dataUrl);
    $.when(dataPromise).done(function(results){
      _this.onDataLoad(results)
    });
  };

  App.prototype.changeFloor = function(floor){
    $(".floor").removeClass("selected");
    $('.floor[data-floor="'+floor+'"]').addClass("selected");
  };

  App.prototype.loadUI = function(){
    var _this = this;

    // load slider
    var $handle = $("#custom-handle");
    $("#slider").slider({
      min: _this.yearStart,
      max: _this.yearEnd,
      value: _this.opt.startYear,
      create: function() {
        var value = $(this).slider("value");
        $handle.text(value);
        _this.onSlide(value);
      },
      slide: function( event, ui ) {
        $handle.text(ui.value);
        _this.onSlide(ui.value);
      }
    });

    // load floor links
    $(".floor-link").on("click", function(e){
      _this.changeFloor($(this).attr("data-floor"))
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
    });
  };

  App.prototype.renderExpeditions = function(data){
    if (data.length > this.opt.maxItems) {
      data = data.slice(0, this.opt.maxExpeditions);
    }

    var items = [];
    var itemData = this.data.expeditions;
    _.each(data, function(index){
      items.push(itemData[index]);
    });

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
      $items.append($('<img src="'+item.image+'" class="'+selected+' floor" data-floor="'+(i+1)+'" alt="Floor plan '+(i+1)+'" />'))
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

  return App;

})();

$(function() {
  var app = new App({});
});
