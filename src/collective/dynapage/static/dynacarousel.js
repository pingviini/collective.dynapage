(function() {

  jQuery(function($) {
    return $("form.dynacarouselForm").each(function() {
      var buttons, cache, carousel, carousel_id, container, content_ids, current_id, default_delay, getNextId, getPrevId, indexOf, next, option, preloadChangingContent, prev, timeout, updateChangingContent, updateSelectedButton;
      carousel = $(this);
      carousel_id = carousel.attr("id");
      container = carousel.parent();
      current_id = container.children(".dynacarousel:first").attr("id");
      content_ids = (function() {
        var _i, _len, _ref, _results;
        _ref = carousel.find("option");
        _results = [];
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          option = _ref[_i];
          _results.push($(option).val());
        }
        return _results;
      })();
      cache = {};
      default_delay = parseInt((carousel.children("input[name='delay']")).attr("value"), 10) * 1000;
      indexOf = function(obj, arr) {
        return (Array.prototype.indexOf || function(obj) {
          var i, _ref;
          for (i = 0, _ref = this.length; 0 <= _ref ? i < _ref : i > _ref; 0 <= _ref ? i++ : i--) {
            if (this[i] === obj) return i;
          }
          return -1;
        }).call(arr, obj);
      };
      getPrevId = function() {
        var _ref;
        return (_ref = content_ids[indexOf(current_id, content_ids) - 1]) != null ? _ref : content_ids[content_ids.length - 1];
      };
      getNextId = function() {
        var _ref;
        return (_ref = content_ids[indexOf(current_id, content_ids) + 1]) != null ? _ref : content_ids[0];
      };
      timeout = false;
      preloadChangingContent = function(content_id, delay, right_to_left) {
        var form, load, url;
        if (delay == null) delay = default_delay;
        if (right_to_left == null) right_to_left = true;
        form = $("#" + carousel_id);
        url = form.attr("action") + ("?ajax_load=1&id=" + content_id);
        load = function(data) {
          var html;
          html = $(data).find(".dynacarousel:first").css({
            position: "absolute",
            top: 0,
            left: 0,
            "z-index": 0
          }).hide().parent().html();
          form.replaceWith(html);
          container.removeClass("busy");
          if (!delay) {
            while (container.find(":animated").length) {
              container.find(":animated").stop(false, true);
            }
          }
          clearTimeout(timeout);
          return timeout = setTimeout((function() {
            return updateChangingContent(delay, right_to_left);
          }), delay);
        };
        if (url in cache) {
          return load(cache[url]);
        } else {
          if (!delay) container.addClass("busy");
          return $.get(url, function(data) {
            return load(cache[url] = data);
          });
        }
      };
      updateChangingContent = function(delay, right_to_left) {
        var busy, current_idx, form, next, next_id, next_idx, other, paused, width;
        if (delay == null) delay = default_delay;
        if (right_to_left == null) right_to_left = true;
        form = $("#" + carousel_id);
        next = form.siblings(".dynacarousel:last");
        next_id = next.attr("id");
        other = next.siblings(".dynacarousel");
        busy = container.find(":animated").length > 0;
        paused = container.hasClass("paused");
        if (next && !busy && (!paused || delay === 0)) {
          if (delay > 0) {
            next.show(0, function() {
              return other.fadeTo(1000, 0, function() {
                next.css({
                  position: "relative",
                  "z-index": 1
                });
                other.remove();
                return updateSelectedButton();
              });
            });
          } else {
            next_idx = indexOf(next_id, content_ids);
            current_idx = indexOf(current_id, content_ids);
            if (next_idx === current_idx) {
              next.css({
                position: "relative",
                "z-index": 1
              });
              next.show(0, function() {
                return other.remove();
              });
            } else if (right_to_left) {
              width = container.innerWidth();
              next.css({
                position: "absolute",
                top: 0,
                left: width,
                "z-index": 1
              });
              next.show(0, function() {
                other.first().animate({
                  left: -width
                }, 500, function() {
                  return other.hide();
                });
                return next.animate({
                  left: 0
                }, 500, function() {
                  next.css({
                    position: "relative"
                  });
                  other.hide(10, function() {
                    return other.remove();
                  });
                  return updateSelectedButton();
                });
              });
            } else {
              width = container.innerWidth();
              next.css({
                position: "absolute",
                top: 0,
                left: -width
              });
              next.show(0, function() {
                other.first().animate({
                  left: width
                }, 500, function() {
                  return other.hide();
                });
                return next.animate({
                  left: 0
                }, 500, function() {
                  next.css({
                    position: "relative",
                    "z-index": 1
                  });
                  other.hide(10, function() {
                    return other.remove();
                  });
                  return updateSelectedButton();
                });
              });
            }
          }
          current_id = next_id;
          clearTimeout(timeout);
          return timeout = setTimeout((function() {
            return preloadChangingContent(getNextId());
          }), 0);
        } else if (next) {
          clearTimeout(timeout);
          return timeout = setTimeout((function() {
            return updateChangingContent();
          }), default_delay);
        }
      };
      updateSelectedButton = function() {
        return container.find(".dynacarousel-selector > span").eq(indexOf(current_id, content_ids)).siblings().removeClass("selected").end().addClass("selected");
      };
      if (carousel.find("input[name='controls']").length > 0) {
        prev = $('<span class="dynacarousel-previous"><span>&lt;</span></span>');
        prev.addClass("visualNoPrint");
        prev.click(function() {
          return preloadChangingContent(getPrevId(), 0, false);
        });
        next = $('<span class="dynacarousel-next"><span>&gt;</span></span>');
        next.addClass("visualNoPrint");
        next.click(function() {
          return preloadChangingContent(getNextId(), 0, true);
        });
        container.addSwipeEvents().bind("swiperight", function(evt, touch) {
          return preloadChangingContent(getPrevId(), 0, false);
        }).bind("swipeleft", function(evt, touch) {
          return preloadChangingContent(getNextId(), 0, true);
        });
        buttons = $('<div class="dynacarousel-selector"></div>');
        buttons.addClass("visualNoPrint");
        $(content_ids).each(function(idx) {
          var link;
          link = $('<span></span>');
          link.click(function() {
            if (idx < indexOf(current_id, content_ids)) {
              preloadChangingContent(content_ids[idx], 0, false);
            } else {
              preloadChangingContent(content_ids[idx], 0, true);
            }
            link.addClass("selected");
            return link.siblings().removeClass("selected");
          });
          return buttons.append(link);
        });
        container.prepend(buttons).prepend(next).prepend(prev);
        updateSelectedButton();
      }
      carousel.siblings(".dynacarousel").css({
        position: "relative",
        "z-index": 1
      });
      container.addClass("dynacarouselWrapper").hover(function() {
        return $(this).addClass("paused");
      }, function() {
        return $(this).removeClass("paused");
      });
      return preloadChangingContent(getNextId());
    });
  });

}).call(this);
