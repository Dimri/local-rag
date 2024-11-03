import { Route, Routes } from "react-router-dom";
import FileUpload from "./FileUpload";
import PDFViewer from "./PDFViewer";

const App = () => {
  return (
    <Routes>
      <Route path="/" element={<FileUpload />} />
      <Route path="/view-pdf" element={<PDFViewer />} />
    </Routes>
  );
};

export default App;
