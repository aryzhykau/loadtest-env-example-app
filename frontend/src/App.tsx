import { useState } from 'react';
import {
  Container,
  CssBaseline,
  ThemeProvider,
  createTheme,
  Box,
  AppBar,
  Toolbar,
  Typography,
  Tabs,
  Tab,
} from '@mui/material';
import Dashboard from './components/Dashboard';
import DataManager from './components/DataManager';
import TaskRunner from './components/TaskRunner';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`tabpanel-${index}`}
      aria-labelledby={`tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

function App() {
  const [tabValue, setTabValue] = useState(0);

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ flexGrow: 1 }}>
        <AppBar position="static">
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              LoadTest Demo Application
            </Typography>
          </Toolbar>
        </AppBar>
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
          <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tabs value={tabValue} onChange={handleTabChange}>
              <Tab label="Dashboard" />
              <Tab label="Data Manager" />
              <Tab label="Task Runner" />
            </Tabs>
          </Box>
          <TabPanel value={tabValue} index={0}>
            <Dashboard />
          </TabPanel>
          <TabPanel value={tabValue} index={1}>
            <DataManager />
          </TabPanel>
          <TabPanel value={tabValue} index={2}>
            <TaskRunner />
          </TabPanel>
        </Container>
      </Box>
    </ThemeProvider>
  );
}

export default App;
