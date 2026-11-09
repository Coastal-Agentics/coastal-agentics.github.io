/* Coastal Agentics: play and pause for the homepage films.
 * Posters stay up unless a clip is allowed to play. Autoplay is desktop-only,
 * and it stays off for reduced motion, reduced data, and Save-Data.
 * A clip pauses off-screen so a phone does not keep decoding it.
 * Remove the script tag and the videos fall back to native controls.
 */
(function () {
  'use strict';

  var videos = Array.prototype.slice.call(document.querySelectorAll('video[data-coastal-video]'));
  if (!videos.length || !window.matchMedia) return;

  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)');
  var narrow = window.matchMedia('(max-width: 899px)');
  var reducedData = window.matchMedia('(prefers-reduced-data: reduce)');
  var ratios = {};

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
    label(video);
  });

  function savesData() {
    return !!(navigator.connection && navigator.connection.saveData);
  }

  function autoplayAllowed() {
    return !reduce.matches && !narrow.matches && !reducedData.matches && !savesData();
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

    var allowAmbient = autoplayAllowed();
    videos.forEach(function (video) {
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
