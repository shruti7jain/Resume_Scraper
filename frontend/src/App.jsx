import Home from './pages/Home';
import './index.css';
import './App.css'; // Just in case there are custom rules there, though index.css has our design system

function App() {
  return (
    <div className="min-h-screen">
      <Home />
    </div>
  );
}

export default App;
