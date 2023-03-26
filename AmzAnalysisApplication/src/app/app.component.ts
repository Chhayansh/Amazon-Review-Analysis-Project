import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';



import * as AOS from 'aos';
import 'aos/dist/aos.css';


@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  title = 'AmzAnalysisApplication';
  url:string=""
  ErrCode:any=""
  ErrString:string=""
  Report:any=''
  loader:boolean=false
  PosReview:boolean=false
  ModReview:boolean=false
  NegReview:boolean=false
  resultDIV:boolean=false
  ErrorDIV:boolean=false
  constructor(private http: HttpClient) { }


    ngOnInit(): void {
      AOS.init();
      console.log("https://www.amazon.in/Godrej-Refrigerator-EDGE-205B-WRF/dp/B0BS6XQVD1/ref=sr_1_10?refinements=p_85%3A10440599031&rps=1&s=kitchen&sr=1-10")
      console.log("https://www.amazon.in/Whirlpool-Inverter-Direct-Cool-Refrigerator-Technology/dp/B0BSRV8C8Y/ref=sr_1_9?refinements=p_85%3A10440599031&rps=1&s=kitchen&sr=1-9")
    }


  onSubmit() {
    this.resultDIV=false
    this.ErrorDIV=false
    this.PosReview=false
    this.NegReview=false
    this.ModReview=false
    this.analyze();
    
  }
  analyze() {
    if(this.url==""){
      this.ErrCode="No Input Found"
      this.ErrString="Enter the URL In the Input Box"
      this.ErrorDIV=true
    }
    else{
    const data = {
      url: this.url,
    };
    this.loader=true
    // console.log("request Send",data)
    this.http.post('http://127.0.0.1:8000/analyze_review', data).subscribe(
      (response) => {
        this.Report= response;
        console.log(this.Report)
        this.loader=false
        // console.log(this.Report.AnalysisResult);
          if (this.Report.AnalysisResult == "I recommend investing in the product as it would be a beneficial use of your money.") {
            this.PosReview=true
          } else if (this.Report.AnalysisResult == "I would strongly suggest against investing in this product") {
            this.NegReview=true
          } else {
            this.ModReview=true
          }
        if(this.Report.PageStatus !== 200){
          this.resultDIV=false
          this.ErrCode=this.Report.PageStatus
          this.ErrString=this.Report.PageStatusString
          this.ErrorDIV=true
        }
        else{
          this.resultDIV=true
        }        
      },
      (error) => {
        this.loader=false
        this.ErrCode=error.status
        this.ErrString=error.statusText
        this.ErrorDIV=true
        console.error('Error:', error);
      }
    );
  }
  }

  Retry() {
    window.location.reload();
}
}

