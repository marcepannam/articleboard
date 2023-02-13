import { Button, Dropdown } from 'antd';
import 'antd/dist/reset.css';
import './App.css';
import { AddArticleFromUrl } from './AddArticleFromUrl';
import { DashboardEditModal } from './DashboardEditModal';
import { Dashboard } from './Dashboard';
import { useHttp } from './UseHttp';

// import { Form, Formik, Field, FormikValues } from 'formik';
import {useState, useCallback } from 'react';

import {
    BrowserRouter as Router,
    Routes,
    Route,
    Link,
    useLocation,
} from "react-router-dom";
import userEvent from '@testing-library/user-event';

export default function App() {
  return (
    <Router>
      <Main/>
    </Router>
  );
}

function Main() {
    const location = useLocation();
    const search = new URLSearchParams(location.search);
    let [loading, dashboards, refresh] = useHttp('/dashboards');

    let [newDashboardModalIsOpen, setNewDashboardModalIsOpen] = useState(false)
    
    let newDashboard = useCallback(() => {
	setNewDashboardModalIsOpen(true)
    }, []) ;

    let hideDashboardEditModal = useCallback(() => setNewDashboardModalIsOpen(false), [setNewDashboardModalIsOpen]);
    
    if (loading || dashboards === null) return <div>loading...</div>;

    let dashboardMenuItems = dashboards.dashboards.map((o : any) => (
	{
	    key: o.id,
	    label: <Link to={"/app/dashboard?id=" + o.id}>{o.title}</Link>
	}));
    
    dashboardMenuItems.push({key:'add', label: 
	<Button onClick={newDashboard}>
		New dashboard
	</Button>})

	let registration = [{
	    key: 'log_out',
	    label: <a href="/accounts/logout/">Log Out</a>
	},
	{
	    key: 'change_password',
	    label: <a href="/accounts/password_change/">Change Password</a>
	}
	]
    
    return (
	<div id="main">    
		<div id='menu'>
			<div id="menu-title">
				<Link
				className='button-text' 
				to='/app/dashboard?id=all'
				>
					Article Recommender
				</Link>
			</div>
			
			<div className='space'/>

			<nav className='buttons'>

				<Button className='menu-button'>
					<Link 
						className='button-text' 
						to={'/app/dashboard?id=all'}>
						Main page
					</Link>
				</Button>
				<Dropdown  
					className='menu-button'
					menu={{items: dashboardMenuItems}}>
					<Button
						className='button-text' 
					>
						Dashboards
					</Button>
				</Dropdown>
				<Button className='menu-button'>
					<Link 
						className='button-text' 
						to="/app/add-article-from-url"
						>
						Add article from URL
					</Link>
				</Button>
				<Dropdown  
				className='menu-button'
				menu={{items: registration}}>
				<Button
					className='button-text' 
				>
					Profile
				</Button>
			</Dropdown>
			</nav>
		</div>
		
		<div id='content'>
			{newDashboardModalIsOpen ?
			<DashboardEditModal id={null} onHide={hideDashboardEditModal} refreshDasboardList={refresh} />
			: null}
			<Routes>
				<Route path="/app/" element={
					<Dashboard
						key={"all"}
						id={"all"}
						filter={"new"}/>}/>
				<Route path="/app/dashboard" element={
					<Dashboard
						key={search.get('id')}
						id={search.get("id")!}
						filter={search.get("filter")}/>}/>
				<Route path="/app/add-article-from-url"
				element={<AddArticleFromUrl dashboards={dashboards.dashboards} />} />
			</Routes>
		</div>

	</div>
  );
}

