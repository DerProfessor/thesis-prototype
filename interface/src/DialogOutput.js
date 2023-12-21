import React, { useEffect, useRef } from "react";
import withStyles from "@material-ui/core/styles/withStyles";
import Typography from "@material-ui/core/Typography";

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

    const audioRef = useRef(null);

    //const paragraphs = data.split("\n");
    const handlePlay = () => {
        audioRef.current.play();
    }

    const audioFileName = "../response.wav"

    return (
        <div>
            <h4>Dialog output:</h4>
            <div>
                <Typography variant="body1" component="p">
                {data}
                </Typography>
            </div>
            <div>
                <button onClick={handlePlay}>Play Audio</button>
                <audio ref={audioRef} controls>
                    <source src={audioFileName} type="audio/wav" />
                    Your browser does not support the audio element.
                </audio>
            </div>
            <div ref={transcriptEndRef}></div>
        </div>
    );
};

export default withStyles(useStyles)(DialogOutput);
