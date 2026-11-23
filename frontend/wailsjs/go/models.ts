export namespace crawler {
	
	export class LogEvent {
	    timestamp: string;
	    level: string;
	    message: string;
	    url: string;
	
	    static createFrom(source: any = {}) {
	        return new LogEvent(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.timestamp = source["timestamp"];
	        this.level = source["level"];
	        this.message = source["message"];
	        this.url = source["url"];
	    }
	}
	export class Metrics {
	    isRunning: boolean;
	    pagesCrawled: number;
	    pagesPerSecond: number;
	    queueSize: number;
	    totalBloomCount: number;
	    bloomMemoryBytes: number;
	    bloomFpRate: number;
	    totalIndexedDocs: number;
	    totalUniqueTerms: number;
	    currentUrl: string;
	    recentLogs: LogEvent[];
	
	    static createFrom(source: any = {}) {
	        return new Metrics(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.isRunning = source["isRunning"];
	        this.pagesCrawled = source["pagesCrawled"];
	        this.pagesPerSecond = source["pagesPerSecond"];
	        this.queueSize = source["queueSize"];
	        this.totalBloomCount = source["totalBloomCount"];
	        this.bloomMemoryBytes = source["bloomMemoryBytes"];
	        this.bloomFpRate = source["bloomFpRate"];
	        this.totalIndexedDocs = source["totalIndexedDocs"];
	        this.totalUniqueTerms = source["totalUniqueTerms"];
	        this.currentUrl = source["currentUrl"];
	        this.recentLogs = this.convertValues(source["recentLogs"], LogEvent);
	    }
	
		convertValues(a: any, classs: any, asMap: boolean = false): any {
		    if (!a) {
		        return a;
		    }
		    if (a.slice && a.map) {
		        return (a as any[]).map(elem => this.convertValues(elem, classs));
		    } else if ("object" === typeof a) {
		        if (asMap) {
		            for (const key of Object.keys(a)) {
		                a[key] = new classs(a[key]);
		            }
		            return a;
		        }
		        return new classs(a);
		    }
		    return a;
		}
	}

}

export namespace db {
	
	export class DBStats {
	    totalDocuments: number;
	    totalTerms: number;
	    totalPostings: number;
	
	    static createFrom(source: any = {}) {
	        return new DBStats(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.totalDocuments = source["totalDocuments"];
	        this.totalTerms = source["totalTerms"];
	        this.totalPostings = source["totalPostings"];
	    }
	}
	export class SearchResult {
	    documentId: number;
	    url: string;
	    title: string;
	    snippet: string;
	    score: number;
	    wordCount: number;
	    matchedTerms: string[];
	
	    static createFrom(source: any = {}) {
	        return new SearchResult(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.documentId = source["documentId"];
	        this.url = source["url"];
	        this.title = source["title"];
	        this.snippet = source["snippet"];
	        this.score = source["score"];
	        this.wordCount = source["wordCount"];
	        this.matchedTerms = source["matchedTerms"];
	    }
	}

}

