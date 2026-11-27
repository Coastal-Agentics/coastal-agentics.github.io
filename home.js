/* Coastal Agentics: play and pause for the homepage films.
 * Posters stay up unless a clip is allowed to play. Autoplay is desktop-only,
 * and it stays off for reduced motion, reduced data, and Save-Data.
 * A clip pauses off-screen so a phone does not keep decoding it.
 * Remove the script tag and the videos fall back to native controls.
 * A video with data-sound-src (the homepage demo reel) also gets Sound on:
 * it swaps to the with-music file, restarts from 0 with native controls,
 * and a second click swaps back to the silent loop at the same moment.
 * Play on a phone starts the with-music file too. The hero's Watch with sound
 * button (data-sound-cta) does the same as Sound on. Videos this script does
 * not manage (the reel on Videos) are never muted; when one plays, the
 * managed clips pause and ambient autoplay waits until it stops.
 */
(function () {
  'use strict';

  var videos = Array.prototype.slice.call(document.querySelectorAll('video[data-coastal-video]'));
  if (!videos.length || !window.matchMedia) return;

  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)');
  var narrow = window.matchMedia('(max-width: 899px)');
  var reducedData = window.matchMedia('(prefers-reduced-data: reduce)');
  var ratios = {};
  var externalPlaying = false;

  videos.forEach(function (video) {
    var frame = video.closest('.film-frame');
    if (frame) frame.classList.add('is-enhanced');
    video.removeAttribute('controls');
    video.muted = true;
    video.playsInline = true;
    video.addEventListener('play', function () { label(video); });
    video.addEventListener('pause', function () { label(video); });
    var button = frame && frame.querySelector('.video-toggle');
    if (button) button.addEventListener('click', function () { toggle(video); });
    var soundButton = frame && frame.querySelector('.sound-toggle');
    if (soundButton && video.getAttribute('data-sound-src')) {
      soundButton.addEventListener('click', function () {
        if (video.dataset.sound === 'on') soundOff(video);
        else soundOn(video, true);
      });
    }
    label(video);
  });

  // Silent loop range: data-loop-start / data-loop-end (seconds) keep the muted
  // hero loop on the action shots, skipping the opening title card and end card.
  // The with-music reel (Sound on) still plays from 0 with its cards.
  videos.forEach(function (video) {
    var from = parseFloat(video.getAttribute('data-loop-start'));
    var to = parseFloat(video.getAttribute('data-loop-end'));
    if (!(from > 0)) return;
    function silent() { return video.dataset.sound !== 'on'; }
    function jump() { try { video.currentTime = from; } catch (e) {} }
    video.addEventListener('loadedmetadata', function () {
      if (silent() && video.currentTime < from) jump();
    });
    video.addEventListener('timeupdate', function () {
      if (!silent()) return;
      var t = video.currentTime;
      if (t < from - 0.25 || (to > from && t >= to)) jump();
    });
  });

  // Hero button "Watch with sound": same as Sound on, then bring the reel into view.
  Array.prototype.slice.call(document.querySelectorAll('[data-sound-cta]')).forEach(function (cta) {
    var target = document.getElementById(cta.getAttribute('data-sound-cta'));
    if (!target || !target.getAttribute('data-sound-src')) return;
    cta.addEventListener('click', function (event) {
      event.preventDefault();
      soundOn(target, true);
      var frame = target.closest('.film-frame') || target;
      frame.scrollIntoView({ behavior: reduce.matches ? 'auto' : 'smooth', block: 'center' });
      var sound = frame.querySelector('.sound-toggle');
      if (sound) sound.focus({ preventScroll: true });
    });
  });

  // Unmanaged videos (for example the full reel on Videos) keep their sound.
  Array.prototype.slice.call(document.querySelectorAll('video:not([data-coastal-video])')).forEach(function (ext) {
    ext.addEventListener('play', function () {
      externalPlaying = true;
      videos.forEach(pause);
    });
    function done() { externalPlaying = false; sync(); }
    ext.addEventListener('pause', done);
    ext.addEventListener('ended', done);
  });

  function soundLabel(video) {
    var frame = video.closest('.film-frame');
    var b = frame && frame.querySelector('.sound-toggle');
    var on = video.dataset.sound === 'on';
    if (frame) frame.classList.toggle('is-sound', on);
    if (!b) return;
    b.setAttribute('aria-pressed', on ? 'true' : 'false');
    b.setAttribute('aria-label', on ? 'Sound off: back to the silent loop' : 'Sound on: play the demo reel from the start with music');
    var t = b.querySelector('[data-sound-label]');
    if (t) t.textContent = on ? 'Sound off' : 'Sound on';
  }

  function swapSource(video, src) {
    if (!video.dataset.loopSources) video.dataset.loopSources = video.innerHTML;
    Array.prototype.slice.call(video.querySelectorAll('source')).forEach(function (s) { s.remove(); });
    if (src) {
      video.src = src;
    } else {
      video.removeAttribute('src');
      video.innerHTML = video.dataset.loopSources;
    }
    video.load();
  }

  function seekWhenReady(video, t) {
    if (!t) return;
    function go() { try { video.currentTime = Math.min(t, (video.duration || t) - 0.1); } catch (e) {} }
    if (video.readyState >= 1) go();
    else video.addEventListener('loadedmetadata', go, { once: true });
  }

  // Called from a click, so play() with sound is allowed (phones included).
  function soundOn(video, fromStart) {
    var t = fromStart ? 0 : video.currentTime;
    video.dataset.sound = 'on';
    swapSource(video, video.getAttribute('data-sound-src'));
    video.loop = false;
    video.muted = false;
    video.volume = 1;
    video.controls = true;
    seekWhenReady(video, t);
    soundLabel(video);
    delete video.dataset.userPaused;
    video.dataset.userPlayed = 'true';
    videos.forEach(function (other) {
      if (other !== video) { pause(other); delete other.dataset.userPlayed; }
    });
    var pending = video.play();
    if (pending && pending.catch) pending.catch(function () { label(video); });
  }

  function soundOff(video) {
    var t = video.currentTime;
    var wasPlaying = !video.paused;
    delete video.dataset.sound;
    video.muted = true;
    video.controls = false;
    video.loop = true;
    swapSource(video, null);
    seekWhenReady(video, t);
    soundLabel(video);
    label(video);
    if (wasPlaying) {
      var pending = video.play();
      if (pending && pending.catch) pending.catch(function () { label(video); });
    }
  }

  function savesData() {
    return !!(navigator.connection && navigator.connection.saveData);
  }

  function autoplayAllowed() {
    return !externalPlaying && !reduce.matches && !narrow.matches && !reducedData.matches && !savesData();
  }

  function label(video) {
    var frame = video.closest('.film-frame');
    var button = frame && frame.querySelector('.video-toggle');
    if (!button) return;
    var paused = video.paused;
    var name = video.getAttribute('data-title') || 'video';
    button.setAttribute('aria-pressed', paused ? 'false' : 'true');
    button.setAttribute('aria-label', (paused ? 'Play ' : 'Pause ') + name);
    var text = button.querySelector('[data-label]');
    if (text) text.textContent = paused ? 'Play' : 'Pause';
  }

  function pause(video) {
    if (!video.paused) video.pause();
  }

  function start(video) {
    if (!video.paused) return;
    videos.forEach(function (other) {
      if (other !== video) pause(other);
    });
    var pending = video.play();
    if (pending && pending.catch) pending.catch(function () { label(video); });
  }

  function toggle(video) {
    if (video.paused && video.getAttribute('data-sound-src') && video.dataset.sound !== 'on') {
      soundOn(video, false);
      return;
    }
    if (video.paused) {
      delete video.dataset.userPaused;
      video.dataset.userPlayed = 'true';
      videos.forEach(function (other) {
        if (other !== video) delete other.dataset.userPlayed;
      });
      start(video);
    } else {
      video.dataset.userPaused = 'true';
      delete video.dataset.userPlayed;
      pause(video);
    }
  }

  function sync() {
    if (document.hidden) {
      videos.forEach(pause);
      return;
    }

    var best = null;
    var bestRatio = 0.5;
    var pinned = null;
    videos.forEach(function (video) {
      var ratio = ratios[video.id] || 0;
      if (ratio > bestRatio) {
        best = video;
        bestRatio = ratio;
      }
      if (video.dataset.userPlayed && !video.dataset.userPaused && ratio >= 0.35) pinned = video;
    });

    var soundPlaying = videos.some(function (v) { return v.dataset.sound === 'on' && !v.paused; });
    var allowAmbient = autoplayAllowed() && !soundPlaying;
    videos.forEach(function (video) {
      if (video.dataset.sound === 'on') return; // the visitor chose sound; native controls own it now
      var ratio = ratios[video.id] || 0;
      var should = video === pinned || (!pinned && allowAmbient && video === best && !video.dataset.userPaused);
      if (should) start(video);
      else if (!video.paused && (ratio < 0.35 || pinned || !allowAmbient)) pause(video);
    });
  }

  if ('IntersectionObserver' in window) {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        ratios[entry.target.id] = entry.isIntersecting ? entry.intersectionRatio : 0;
      });
      sync();
    }, { threshold: [0, 0.25, 0.5, 0.75, 1] });
    videos.forEach(function (video) { observer.observe(video); });
  }

  function onChange() { sync(); }
  if (reduce.addEventListener) reduce.addEventListener('change', onChange);
  else if (reduce.addListener) reduce.addListener(onChange);
  if (narrow.addEventListener) narrow.addEventListener('change', onChange);
  if (reducedData.addEventListener) reducedData.addEventListener('change', onChange);
  document.addEventListener('visibilitychange', sync);
  window.addEventListener('pagehide', function () { videos.forEach(pause); });
})();
