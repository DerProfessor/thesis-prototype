import React, { useEffect, useRef } from "react";
import withStyles from "@mui/styles/withStyles";
import Typography from "@mui/material/Typography";

const useStyles = () => ({
    root: {
      maxWidth: "800px",
      display: "flex",
    },
    outputText: {
      marginLeft: "8px",
      color: "#ef395a",
    },
  });

const DialogOutput = ({ data, classes }) => {
    const transcriptEndRef = useRef(null);

    const scrollToBottom = () => {
      transcriptEndRef.current.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
      }, [data]);

    return (
        <div>
            <h5>Dialog output:</h5>
            <div>
                <Typography variant="body1" component="p">
                {data}
                </Typography>
            </div>
            <div ref={transcriptEndRef}></div>
        </div>
    );
};

export default withStyles(useStyles)(DialogOutput);
