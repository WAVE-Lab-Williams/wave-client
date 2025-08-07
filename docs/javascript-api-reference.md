## Classes

<dl>
<dt><a href="#WaveClientError">WaveClientError</a></dt>
<dd><p>Error classes for the WAVE JavaScript client</p>
</dd>
</dl>

## Functions

<dl>
<dt><a href="#logExperimentData">logExperimentData(experimentId, participantId, data)</a> ⇒ <code>Promise.&lt;Object&gt;</code></dt>
<dd><p>Primary method: Log experiment data</p>
</dd>
<dt><a href="#getHealth">getHealth()</a> ⇒ <code>Promise.&lt;Object&gt;</code></dt>
<dd><p>Get API health status</p>
</dd>
<dt><a href="#getVersion">getVersion()</a> ⇒ <code>Promise.&lt;Object&gt;</code></dt>
<dd><p>Get API version and compatibility information</p>
</dd>
<dt><a href="#setBaseUrl">setBaseUrl(baseUrl)</a></dt>
<dd><p>Update base URL</p>
</dd>
<dt><a href="#createErrorFromResponse">createErrorFromResponse(response, errorData)</a> ⇒ <code><a href="#WaveClientError">WaveClientError</a></code></dt>
<dd><p>Create appropriate error from HTTP response</p>
</dd>
<dt><a href="#parseRetryAfter">parseRetryAfter(retryAfterHeader)</a> ⇒ <code>number</code></dt>
<dd><p>Parse Retry-After header value to milliseconds</p>
</dd>
</dl>

<a name="logExperimentData"></a>

## logExperimentData(experimentId, participantId, data) ⇒ <code>Promise.&lt;Object&gt;</code>
Primary method: Log experiment data

**Kind**: global function  
**Returns**: <code>Promise.&lt;Object&gt;</code> - Created data row with all fields  

| Param | Type | Description |
| --- | --- | --- |
| experimentId | <code>string</code> | Experiment UUID |
| participantId | <code>string</code> | Participant identifier |
| data | <code>Object</code> | Experiment data matching the experiment type schema |

<a name="getHealth"></a>

## getHealth() ⇒ <code>Promise.&lt;Object&gt;</code>
Get API health status

**Kind**: global function  
**Returns**: <code>Promise.&lt;Object&gt;</code> - Health status  
<a name="getVersion"></a>

## getVersion() ⇒ <code>Promise.&lt;Object&gt;</code>
Get API version and compatibility information

**Kind**: global function  
**Returns**: <code>Promise.&lt;Object&gt;</code> - Version information  
<a name="setBaseUrl"></a>

## setBaseUrl(baseUrl)
Update base URL

**Kind**: global function  

| Param | Type | Description |
| --- | --- | --- |
| baseUrl | <code>string</code> | New base URL |

<a name="createErrorFromResponse"></a>

## createErrorFromResponse(response, errorData) ⇒ [<code>WaveClientError</code>](#WaveClientError)
Create appropriate error from HTTP response

**Kind**: global function  
**Returns**: [<code>WaveClientError</code>](#WaveClientError) - Appropriate error instance  

| Param | Type | Description |
| --- | --- | --- |
| response | <code>Response</code> | Fetch API response |
| errorData | <code>Object</code> | Parsed error response body |

<a name="parseRetryAfter"></a>

## parseRetryAfter(retryAfterHeader) ⇒ <code>number</code>
Parse Retry-After header value to milliseconds

**Kind**: global function  
**Returns**: <code>number</code> - Retry delay in milliseconds  

| Param | Type | Description |
| --- | --- | --- |
| retryAfterHeader | <code>string</code> \| <code>null</code> | Retry-After header value |

