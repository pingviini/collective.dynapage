jQuery ($) ->
  $("form.dynacarouselForm").each ->
    # define context
    carousel = $(this)
    carousel_id = carousel.attr "id"

    container = do carousel.parent

    # read content ids from carousel form fields
    current_id = container.children(".dynacarousel:first").attr "id"
    content_ids = (do $(option).val for option in carousel.find("option"))
    cache = {}

    # read delay form carousel form fields
    default_delay = parseInt(\
      (carousel.children "input[name='delay']").attr("value"), 10) * 1000

    # define indexOf, because IE doesn't have Array.prototype.indexOf yet
    indexOf = (obj, arr) ->
      (Array.prototype.indexOf or (obj) ->
        for i in [0...this.length]
          if this[i] == obj
            return i
        return -1).call(arr, obj)

    # get previous carousel content id
    getPrevId = ->
        return content_ids[indexOf(current_id, content_ids) - 1] ?\
          content_ids[content_ids.length - 1]

    # get next catousel content id
    getNextId = ->
        return content_ids[indexOf(current_id, content_ids) + 1] ? content_ids[0]

    # store timout id to be able to cancel timouts
    timeout = false

    # preload next (or given) carousel item, hide it and time the change
    preloadChangingContent = (content_id, delay=default_delay, right_to_left=true) ->
      form = $("#" + carousel_id)
      url = form.attr("action") + "?ajax_load=1&id=#{content_id}"

      load = (data) ->
        html = $(data).find(".dynacarousel:first")
          .css(position: "absolute", top: 0, left: 0, "z-index": 0).hide()
          .parent().html()
        form.replaceWith(html)
        container.removeClass("busy")
        if not delay
          while container.find(":animated").length
            container.find(":animated").stop(false, true)
        clearTimeout timeout
        timeout =\
          setTimeout (-> updateChangingContent delay, right_to_left), delay

      if url of cache then load cache[url]
      else
        if not delay then container.addClass "busy"
        $.get url, (data) -> load cache[url] = data

    # change the visible carousel item to the next preloaded one
    updateChangingContent = (delay=default_delay, right_to_left=true) ->
      form = $("#" + carousel_id)

      next = form.siblings(".dynacarousel:last")
      next_id = next.attr "id"
      other = next.siblings(".dynacarousel")

      busy = container.find(":animated").length > 0
      paused = container.hasClass "paused"

      if next and not busy and (not paused or delay == 0)
        if delay > 0  # crossfade when there's delay
          next.show 0, ->
            other.fadeTo 1000, 0, ->
              next.css position: "relative", "z-index": 1
              do other.remove
              do updateSelectedButton
        else  # slide left / right for immediate synchronous update
          next_idx = indexOf next_id, content_ids
          current_idx = indexOf current_id, content_ids

          # Dummy swap when ids match
          if next_idx == current_idx
              next.css position: "relative", "z-index": 1
              next.show 0, -> do other.remove
          # Slide in from right (slide out to left) for succeeding item
          else if right_to_left
            width = do container.innerWidth
            next.css position: "absolute", top: 0, left: width, "z-index": 1
            next.show 0, ->
              other.first().animate left: -width, 500, -> do other.hide
              next.animate left: 0, 500, ->
                next.css position: "relative"
                other.hide 10, -> do other.remove
                do updateSelectedButton
          # Slide in from left (slide out to right) for preceding item
          else
            width = do container.innerWidth
            next.css position: "absolute", top: 0, left: -width
            next.show 0, ->
              other.first().animate left: width, 500, -> do other.hide
              next.animate left: 0, 500, ->
                next.css position: "relative", "z-index": 1
                other.hide 10, -> do other.remove
                do updateSelectedButton

        # Update current_id and preload the next item
        current_id = next_id
        clearTimeout timeout
        timeout = setTimeout (-> preloadChangingContent do getNextId), 0
      else if next
        # Try again after the delay
        clearTimeout timeout
        timeout = setTimeout (-> do updateChangingContent), default_delay

    updateSelectedButton = ->
      container.find(".dynacarousel-selector > span")
        .eq(indexOf(current_id, content_ids))
        .siblings().removeClass("selected").end()
        .addClass("selected")

    # Create and wire navigation
    if carousel.find("input[name='controls']").length > 0
      prev = $('<span class="dynacarousel-previous"><span>&lt;</span></span>')
      prev.addClass "visualNoPrint"
      prev.click -> preloadChangingContent do getPrevId, 0, false

      next = $('<span class="dynacarousel-next"><span>&gt;</span></span>')
      next.addClass "visualNoPrint"
      next.click -> preloadChangingContent do getNextId, 0, true

      container.addSwipeEvents()
        .bind("swiperight", (evt, touch) ->
          preloadChangingContent do getPrevId, 0, false)
        .bind("swipeleft", (evt, touch) ->
          preloadChangingContent do getNextId, 0, true)

      # Buttons
      buttons = $('<div class="dynacarousel-selector"></div>')
      buttons.addClass "visualNoPrint"
      $(content_ids).each (idx) ->
        link = $('<span></span>')
        link.click ->
          if idx < indexOf(current_id, content_ids)
            preloadChangingContent content_ids[idx], 0, false
          else
            preloadChangingContent content_ids[idx], 0, true
          link.addClass "selected"
          link.siblings().removeClass "selected"
        buttons.append link

      container.prepend(buttons).prepend(next).prepend(prev)

      do updateSelectedButton

    # Prepare the initial content
    carousel.siblings(".dynacarousel")
      .css position: "relative", "z-index": 1
    container.addClass("dynacarouselWrapper").hover(
        -> $(this).addClass "paused"
        -> $(this).removeClass "paused"
      )

    # Go
    preloadChangingContent do getNextId
