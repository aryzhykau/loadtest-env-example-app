import { useQuery } from '@tanstack/react-query';
import {
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  Storage as StorageIcon,
  Task as TaskIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';
import { getHealth, getMetrics } from '../services/api';

export default function Dashboard() {
  const { data: health, isLoading: healthLoading, error: healthError } = useQuery({
    queryKey: ['health'],
    queryFn: getHealth,
    refetchInterval: 5000,
  });

  const { data: metrics, isLoading: metricsLoading } = useQuery({
    queryKey: ['metrics'],
    queryFn: getMetrics,
    refetchInterval: 5000,
  });

  if (healthLoading || metricsLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (healthError) {
    return (
      <Alert severity="error">
        Failed to connect to backend. Please ensure the API server is running.
      </Alert>
    );
  }

  const getStatusColor = (status: string): 'success' | 'error' | 'warning' => {
    if (status.includes('connected')) return 'success';
    if (status.includes('error')) return 'error';
    return 'warning';
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        System Dashboard
      </Typography>

      {/* Health Status */}
      <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
        Health Status
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                MongoDB
              </Typography>
              <Chip
                label={health?.mongodb || 'unknown'}
                color={getStatusColor(health?.mongodb || '')}
                size="small"
              />
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Redis
              </Typography>
              <Chip
                label={health?.redis || 'unknown'}
                color={getStatusColor(health?.redis || '')}
                size="small"
              />
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Celery
              </Typography>
              <Chip
                label={health?.celery || 'unknown'}
                color={getStatusColor(health?.celery || '')}
                size="small"
              />
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Overall
              </Typography>
              <Chip
                label={health?.status || 'unknown'}
                color={health?.status === 'healthy' ? 'success' : 'error'}
                size="small"
              />
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Metrics */}
      <Typography variant="h6" gutterBottom sx={{ mt: 4 }}>
        Application Metrics
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={4}>
          <Paper sx={{ p: 3, display: 'flex', alignItems: 'center' }}>
            <StorageIcon sx={{ fontSize: 40, mr: 2, color: 'primary.main' }} />
            <Box>
              <Typography color="textSecondary" variant="body2">
                Data Entries
              </Typography>
              <Typography variant="h4">{metrics?.total_data_entries || 0}</Typography>
            </Box>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <Paper sx={{ p: 3, display: 'flex', alignItems: 'center' }}>
            <TaskIcon sx={{ fontSize: 40, mr: 2, color: 'info.main' }} />
            <Box>
              <Typography color="textSecondary" variant="body2">
                Total Tasks
              </Typography>
              <Typography variant="h4">{metrics?.total_tasks || 0}</Typography>
            </Box>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <Paper sx={{ p: 3, display: 'flex', alignItems: 'center' }}>
            <CheckCircleIcon sx={{ fontSize: 40, mr: 2, color: 'success.main' }} />
            <Box>
              <Typography color="textSecondary" variant="body2">
                Completed Tasks
              </Typography>
              <Typography variant="h4">{metrics?.completed_tasks || 0}</Typography>
            </Box>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <Paper sx={{ p: 3, display: 'flex', alignItems: 'center' }}>
            <CircularProgress size={40} sx={{ mr: 2 }} />
            <Box>
              <Typography color="textSecondary" variant="body2">
                Active Tasks
              </Typography>
              <Typography variant="h4">{metrics?.active_tasks || 0}</Typography>
            </Box>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <Paper sx={{ p: 3, display: 'flex', alignItems: 'center' }}>
            <ErrorIcon sx={{ fontSize: 40, mr: 2, color: 'error.main' }} />
            <Box>
              <Typography color="textSecondary" variant="body2">
                Failed Tasks
              </Typography>
              <Typography variant="h4">{metrics?.failed_tasks || 0}</Typography>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
