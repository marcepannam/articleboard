import { Button, Spin} from 'antd';
import 'antd/dist/reset.css';
import './App.css';
import './Dashboard.css'
import { useState, useCallback, useEffect } from 'react';
import { useHttp } from './UseHttp';
import { DashboardEditModal} from './DashboardEditModal'
import { Article } from './Article';
import { Link } from "react-router-dom";


export function Dashboard({ id, filter } : {id : string; filter: string | null}) {
    let filter_ = filter ?? "new";
    
    let [loading, dashboard, refresh] = useHttp('/dashboard?id=' + escape(id) + "&filter=" + escape(filter_));

    let [removedIds, setRemovedIds] = useState(new Map());
    
    function link(newFilter:string) { return "/app/dashboard?id=" + escape(id) + "&filter=" + escape(newFilter) }

    let labelChanged = useCallback((removedId : string) => {
	setRemovedIds((ids) => {
	    let newIds = new Map(ids);
	    newIds.set(removedId, true)
	    return newIds
	});
    }, [])
    
    let [editModalIsOpen, setEditModalIsOpen] = useState(false);
    
    let hideDashboardEditModal = useCallback(() => { setEditModalIsOpen(false); refresh() }, [setEditModalIsOpen])
    let showDashboardEditModal = useCallback(() => { setEditModalIsOpen(true); }, [setEditModalIsOpen])    

    let dashboardEmpty = !dashboard?.articles || dashboard.articles.every((article:{id:string}) => (
        removedIds.get(article.id) == true   
    ));

    useEffect(() => {
        if (!loading && dashboardEmpty)
            setTimeout(() => refresh(), 1000);
    }, [loading, dashboardEmpty]);

    if(dashboardEmpty){ 
        
        if(id==='all'){
        return <div className='loading empty-dashboard'> Please create a first dashboard to get recommendations.</div>}
        else{


           return (
           <div className="loading">
                <Spin size="large"/> 
                &nbsp;&nbsp;Loading new recommendations...
           </div>);
        }
    }

    if (loading || dashboard === null)
    {
     return  (
     <div className='loading'>
        <Spin size="large"/> 
        Loading...
        </div>
     );	     
    }


    return <div className="content-body">
	       {editModalIsOpen ?
		<DashboardEditModal
		    id={id} onHide={hideDashboardEditModal}
		    dashboard={dashboard}
		/>
		: null}

	       <h1 id='dashboard-title'>{dashboard.dashboard_title}</h1>
            <div id='filters-with-settings'>
                <div id='filters'>
                    <span>Show: &nbsp;</span>
                    <Link className='filter' to={link('new')}>
                        new
                    </Link><span> &nbsp;|&nbsp; </span>
                    <Link className='filter' to={link('liked')}>
                        only liked
                    </Link><span>&nbsp; |&nbsp; </span>
                    <Link className='filter' to={link('disliked')}>
                        only disliked
                    </Link>
                </div>
                <div id='settings'>
                    {id != 'all' ? <>
                        <Button className='green-button' onClick={showDashboardEditModal}>
                            Settings
                        </Button></> : null}
                </div>
            </div>
           <div>
		   { dashboard.articles.map((article : any) =>
		       <div className={(filter_ === 'new' && removedIds.get(article.id)) ? "article-hidden" : "article-not-hidden"} key={article.id}>
			   <Article article={article} labelChanged={labelChanged} showDashboard={id === "all"} />
		       </div>
		       ) }
	       </div>
	   </div>
}