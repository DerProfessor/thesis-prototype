import React, { useEffect } from "react";
import withStyles from "@mui/styles/withStyles";

const useStyles = () => ({
  errorPopup: {
    backgroundColor: "#ff0000",
    color: "#ffffff",
    padding: "10px 20px",
    borderRadius: "10px",
    boxShadow: "0px 2px 4px rgba(0, 0, 0, 0.2)",
    marginBottom: "20px",
  },
});

const ErrorMessage = ({ classes, messages, setErrorMessages }) => {
  useEffect(() => {
    const timer = setTimeout(() => {
      // Automatically clear the error message after 5 seconds
      setErrorMessages(null);
    }, 5000);

    return () => {
      clearTimeout(timer);
    };
  }, []);

  return (
    <div>
      {messages.map((message, index) => (
        <div key={index} className={classes.errorPopup}>
          {message}
        </div>
      ))}
    </div>
  );
};

export default withStyles(useStyles)(ErrorMessage);
