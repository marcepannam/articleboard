import 'antd/dist/reset.css';
import './App.css';
import { baseUrl } from './Consts';
import {useState, useEffect, useCallback } from 'react';

export function useHttp(url : string) : [boolean, any, () => void] {
    let [response, setResponse] = useState(null);
    let [loading, setLoading] = useState(true);

    let fetchData = async () => {
        setLoading(true);
        const response = await fetch(
            baseUrl + url,
	    {
		credentials: "include"
	    }
        );
	if (response.status === 401) {
	    window.location.href = "/accounts/login/?next=" + escape(window.location.href);
            return;
	}
        const data = await response.json();
        setResponse(data);
        setLoading(false);
    };
    
    let refresh = useCallback(() => {
	fetchData().catch(console.error);
    }, [url]);
    
    useEffect(() => { 
        // useEffect calls fetchData each time url changes
	    fetchData().catch(console.error);
    }, [url]);
    
    return [loading, response, refresh];
}
