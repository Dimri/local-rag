import React from "react";
import { Document, Page, Text, View, StyleSheet } from "@react-pdf/renderer";

// Define your PDF document's styles
const styles = StyleSheet.create({
  page: {
    flexDirection: "column",
    backgroundColor: "#ffffff",
  },
  section: {
    margin: 10,
    padding: 10,
    flexGrow: 1,
  },
});

// Define your PDF document layout
const PDFDocument = ({ fileName }) => (
  <Document>
    <Page style={styles.page}>
      <View style={styles.section}>
        <Text>Displaying PDF: {fileName}</Text>
      </View>
    </Page>
  </Document>
);

export default PDFDocument;
