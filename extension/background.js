/* BareBones Projects, Designed by: Justin Levesque-Welsch */
chrome.runtime.onInstalled.addListener(()=>chrome.contextMenus.create({id:'omarchy-create-skill',title:'Create Omarchy Skill from selected text',contexts:['selection']}));
chrome.contextMenus.onClicked.addListener((info)=>{if(info.menuItemId==='omarchy-create-skill' && info.selectionText){chrome.tabs.create({url:'http://127.0.0.1:8765/?draft='+encodeURIComponent(info.selectionText.slice(0,200000))})}});
