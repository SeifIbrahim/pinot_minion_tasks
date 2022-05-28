"use strict";
/*jshint esversion: 9 */
/* jshint -W097 */

// default url where report server is located
const quality_change_url = "http://localhost:34543/quality";
const state_change_url = "http://localhost:34543/state";
const stats_url = "http://localhost:34543/report";
const meta_url = "http://localhost:34543/meta";
const report_time = 250;

const PLAYING_STATE = 1;

let start_play_time;
let started = false;

document.addEventListener("keyup",  event => {
    if (event.code === "Space") {
        console.log("Started video");
        start_play_time = Date.now();
    }
});

function postReport(url, jsonData) {
    // this function sends json data to report server
    let xhr = new XMLHttpRequest();
    xhr.open("POST", url, true);
    xhr.setRequestHeader("Content-Type", "application/json; charset=utf-8");
    xhr.send(JSON.stringify(jsonData));
}

function onStateChange(event) {
    // this function catch player state changes and report them
    postReport(
        state_change_url,
        {
            timestamp: Date.now(),
            video_id_and_cpn: player.getStatsForNerds().video_id_and_cpn,
            fraction: player.getVideoLoadedFraction(),
            current_time: player.getCurrentTime(),
            new_state: event,
        }
    );

    // report startup delay
    if (event == PLAYING_STATE && !started) {
        started = true;
        let startup_delay = Date.now() - start_play_time;
        postReport(
            meta_url,
            {
                timestamp: Date.now(),
                video_id_and_cpn: player.getStatsForNerds().video_id_and_cpn,
                startup_delay: startup_delay,
            }
        );
    }

}

function onPlaybackQualityChange(event) {
    // this function post quality changes
    postReport(
        quality_change_url,
        {
            timestamp: Date.now(),
            video_id_and_cpn: player.getStatsForNerds().video_id_and_cpn,
            fraction: player.getVideoLoadedFraction(),
            current_time: player.getCurrentTime(),
            new_quality: event,
        }
    );
}

function sendStats() {
    // this function is executed every X ms and reports current statistics
    let stats_for_nerds = player.getStatsForNerds();
    stats_for_nerds.playback_fraction = player.getVideoLoadedFraction();
    stats_for_nerds.current_time = player.getCurrentTime();
    stats_for_nerds.timestamp = Date.now();

    postReport(stats_url, stats_for_nerds);
}

// wait until player is ready
while (!document.getElementById("movie_player")) {
    (async () => {
        await new Promise(r => setTimeout(r, 100));
    })();
}

// get the player
let player = document.getElementById("movie_player");

// register callbacks on state and quality changes
player.addEventListener("onStateChange", onStateChange);
player.addEventListener("onPlaybackQualityChange", onPlaybackQualityChange);

// report stats for nerds every X ms
setInterval(sendStats, report_time);
