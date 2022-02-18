var https = require('https');
var jsdom = require('jsdom');
var { JSDOM } = jsdom;
var fs = require('fs');

var startShow = 6500;
var endShow = 6900;
var allShows = [];
while (startShow <= endShow) {
    allShows.push(getShowDataPromise(startShow));
    startShow++;
}

function getShowDataPromise(show) {
    return new Promise((resolve, reject) => {
        var questionsURL = "https://www.j-archive.com/showgame.php?game_id=" + show;
        var responsesURL = "https://www.j-archive.com/showgameresponses.php?game_id=" + show;

        var categoryNames = [];
        var clues = [];

        https.get(questionsURL, (res) => {
            var questionsHTML = '';
            res.on('data', (chunk) => {
                questionsHTML += chunk.toString();
            });
            res.on('end', () => {
                var element = new JSDOM(questionsHTML);
                
                var gameTitle = element.window.document.getElementById('game_title').firstChild.innerHTML;

                var categories = element.window.document.getElementsByClassName('category_name');

                for (var i = 0; i < categories.length; i++) {
                    categoryNames.push(cleanHTML(categories.item(i).innerHTML));
                }

                var allClues = element.window.document.getElementsByClassName('clue_text');

                for (i = 0; i < allClues.length - 1; i++) {
                    var id = allClues.item(i).id;
                    var doubleJeopardy = id.charAt(5) == 'D';

                    var q = cleanHTML(allClues.item(i).innerHTML);
                    var value = parseInt(id.charAt(id.length - 1)) * 200 * (doubleJeopardy ? 2 : 1);
                    var categoryId = parseInt(id.charAt(id.length - 3)) + (doubleJeopardy ? 6 : 0) - 1;

                    var clue = {
                        'clue': q,
                        'value': value,
                        'category': categoryNames[categoryId],
                        'episode': gameTitle
                    }
                    clues.push(clue);
                }

                https.get(responsesURL, (res) => {
                    var responsesHTML = '';
                    res.on('data', (chunk) => {
                        responsesHTML += chunk.toString();
                    });
                    res.on('end', () => {
                        var element = new JSDOM(responsesHTML);
                
                        var allAnswers = element.window.document.getElementsByClassName('correct_response');
                
                        for (i = 0; i < allAnswers.length - 1; i++) {
                            var a = cleanHTML(allAnswers.item(i).innerHTML);
                            clues[i]['answer'] = a;
                        }

                        clues = clues.filter(clue => {
                            return clue['clue'].indexOf('</a>') == -1
                        });

                        fs.writeFile('shows/show' + show + '.json', JSON.stringify(clues), { recursive: true }, (err) => {
                            if (err) reject();
                            resolve();
                        });
                    })
                });
            })
        });
    });
}

var p = Promise.all(allShows);
p.then()

function cleanHTML(myString) {
    myString = myString.replace(/&amp;/ig, '&');
    myString = myString.replace(/<br>/ig, ' ');
    myString = myString.replace(/<\/?i>/ig, '');
    myString = myString.replace(/<\/?span[^>]*>/ig, '');
    return myString;
}
