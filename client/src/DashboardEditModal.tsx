import { Modal, Input, Form, Select } from 'antd';
import 'antd/dist/reset.css';
import './DashboardEditModal.css';
import { baseUrl } from './Consts';
import { getCookie } from './CsrfToken';
import { useCallback } from 'react';
import { useNavigate } from "react-router-dom";
import { useHttp } from './UseHttp';

const csrftoken = getCookie('csrftoken');

export function DashboardEditModal({ id, onHide, refreshDasboardList, dashboard }: { id: null | string, onHide: () => void, refreshDasboardList?: () => void, dashboard?: { keywords: string, dashboard_title: string, notifications: string } }) {
	let saveDashboard = async (values: any) => {

		const response = await fetch(
			baseUrl + '/dashboard' + (id === null ? "" : "?id=" + escape(id)),
			{
			    method: id === null ? 'POST' : 'PUT',
			    credentials: "include",
			    body: "title=" + escape(values.title) + '&keywords=' + escape(values.keywords.join("\n")) + '&notifications=' + escape(values.notifications),
			    headers: { 'X-CSRFToken': csrftoken, 'content-type': 'application/x-www-form-urlencoded' },
			}
		);

		if(refreshDasboardList)
			refreshDasboardList();

		onHide();
		if (id === null) {
			const data = await response.json()
			navigate('/app/dashboard?id=' + escape(data.id))
		}
	};

	let onSubmit = useCallback((values: any) => {
		saveDashboard(values);
	}, [onHide, id]);

	let navigate = useNavigate();

	let handleOk = useCallback(() => {
		form.submit()
	}, [id, onHide]);

	let [form] = Form.useForm();

	let keywordsString = dashboard?.keywords;
	let keywords: string[];
	if (keywordsString) keywords = keywordsString.split("\n");
	else keywords = [];

	let currentKeywords = Form.useWatch('keywords', form);
	currentKeywords = currentKeywords ? currentKeywords.join('\n') : "";
	console.log('keywords:' + currentKeywords)
	let [suggestionsLoading, suggestions, suggestionsRefresh] = useHttp('/suggest-keywords?keywords=' + escape(currentKeywords))
	suggestions = suggestions ? suggestions['words'] : [];

	console.log(suggestions);

	return <Modal
		title={id === null ? "Create new dashboard" : "Edit dashboard"}
		open={true}
		onOk={handleOk}
		onCancel={onHide}>
		<Form
			form={form}
			onFinish={onSubmit}>
			<Form.Item
				name="title"
				label="Title"
				initialValue={dashboard?.dashboard_title}
			>
				<Input />
			</Form.Item>
			<Form.Item name="keywords" label="Keywords"
				initialValue={keywords}>
				<Select
					mode="tags"
					style={{ width: '100%' }}
					tokenSeparators={['\n']}
					placeholder="add keywords"
					options={suggestions.map( (item:string) => ({value:item, label:item}))}
				/>
			</Form.Item>
		        <Form.Item name="notifications" label="Email notifications about new articles"
				   initialValue={dashboard?.notifications}>
				<Select
				    options={[
					{value: 'disabled', label: 'disabled'},
					{value: 'daily', label: 'daily'},
					{value: 'weekly', label: 'weekly'},
					{value: 'monthly', label: 'monthly'},
				    ]} 
				/>
			</Form.Item>
		</Form>
	</Modal>
}
