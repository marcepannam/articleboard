import { Button, Input, Form, Select, Alert, Spin } from 'antd';
import 'antd/dist/reset.css';
import './App.css';
import './AddArticleFromUrl.css';
import { getCookie } from './CsrfToken';
import {baseUrl} from './Consts';

import { useState, useCallback } from 'react';

const csrftoken = getCookie('csrftoken');


export function AddArticleFromUrl({dashboards}: {dashboards: {id:number; title: string}[]}) {
    let [form] = Form.useForm();

    let [state, setState] = useState('none');

    let addArticle = async (url : string, dashboards?: string[]) => {
	setState('loading');
	let responseJson;
	try {
	const response = await fetch(
            baseUrl + '/add-article-from-url',
	    {
		method: 'POST',
		credentials: "include",
		body: "url=" + escape(url) + "&dashboards=" + escape(JSON.stringify(dashboards)),
		headers: {'X-CSRFToken': csrftoken, 'content-type': 'application/x-www-form-urlencoded'},
	    }
        );
	    responseJson = await response.json();
		console.log("response json: ", responseJson);
	} catch(e) {
		//toremove
		console.log('1: ', e)
	    setState('error');
	    throw e;
	}

	if (responseJson.ok) {
	    setState('success');
	    form.resetFields()
	}
	else setState('error')
		//toremove
		console.log('2: json', responseJson)
    };
    
    
    let onSubmit = useCallback((values: any) => {
	console.log(values)
	addArticle(values.url, values.dashboards)
    }, []);
    
    return <div className="content-body url-page-body">
	       <h3>Add article from URL</h3>
	          <Form
		   form={form}
		   onFinish={onSubmit}>
		      <Form.Item name="url" label="URL">
			  <Input />
		      </Form.Item>
		      <Form.Item name="dashboards" label="Add to dashboards">
			  <Select 
			  	mode="multiple"
				tokenSeparators={['\n']}
				options={dashboards.map(({id, title}) => ({value: id, label: title}))}  />
		      </Form.Item>
		      <Button htmlType="submit" disabled={state === 'loading'}>Submit</Button>
		  </Form>
	       { state === 'loading' ? <Spin />  : null}
	       { state === 'error' ? <Alert message="Failed to download article" type="error" />  : null}
		   { state === 'success' ? <Alert  message='Article was successfully added to the liked in the dashboard.'/>:null}
	   </div>;
}
