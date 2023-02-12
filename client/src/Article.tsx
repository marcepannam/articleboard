import { Button } from 'antd';
import 'antd/dist/reset.css';
import './App.css';
import './Article.css';
import { baseUrl } from './Consts';
import { getCookie } from './CsrfToken';
import { useCallback, useState } from 'react';

const csrftoken = getCookie('csrftoken');

export function Article({article, labelChanged, showDashboard}: {
    article : {link:string; short_description:string; added:string; id:string; title:string; dashboard:string},
    showDashboard : boolean,
    labelChanged: (id:string) => void}) {    
    let changeLabel = async (label:string) => {
	await fetch(
            baseUrl + '/article?id=' + escape(article.id),
	    {
		method: 'POST',
		credentials: "include",
		body: "label=" + escape(label),
		headers: {'X-CSRFToken': csrftoken, 'content-type': 'application/x-www-form-urlencoded'},
	    }
        );
	labelChanged(article.id)
    };
    
    let doLike = useCallback(() => { changeLabel('like') }, [article.id, labelChanged]);
    let doDislike = useCallback(() => { changeLabel('dislike') }, [article.id ,labelChanged]);
    let doFlag = useCallback(() => { changeLabel('flag') }, [article.id ,labelChanged]);
    
    return      (
    <div className="article">
        <div className='dashboard-link-container'>
            <div className='flag'>
   	            <Button onClick={doFlag}>flag</Button>
	        </div> 
            {showDashboard ? 
            <div className="dashboard-link">{article.dashboard}</div> : ""} 
        </div>
        <h3 className='article-title'><a href={article.link} target="_blank">{article.title}</a></h3>
        <div className='article-description'>{article.short_description}</div>
        <div className="link">{article.link}</div>
            <div className='green-buttons buttons'>
                <Button className='article-button button button-text' onClick={doLike}>
                    like
                </Button>
                <Button className='article-button button button-text' onClick={doDislike}>
                    dislike
                </Button>
        </div>
    </div>
    )
}
