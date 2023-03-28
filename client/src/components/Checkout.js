import React from "react";

class Checkout extends React.Component {
    constructor(props) {
      super(props);
      this.state = {
        amount: ''
      };
      this.handleSubmit = this.handleSubmit.bind(this);
      this.handleChange = this.handleChange.bind(this);
    }
   
    handleChange(event) {
      this.setState({amount: event.target.amount});
    }
  
    handleSubmit(event) {
      alert('Checked Out: ' + this.state.amount);
      event.preventDefault();
    }

    render() {
      return (
        <form onSubmit={this.handleSubmit}>
          <label>
             Enter Quantity of Hardware:
             <div>
              <input type="text" amount={this.state.amount} onChange={this.handleChange} />
             </div>
          </label>
        <input type="submit" value="Check In" />
        <input type="submit" value="Check Out" />
       </form>
      );
    }
   }

   export default Checkout;