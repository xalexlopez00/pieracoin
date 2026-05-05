package metrics

import (
	"net/http"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
	"github.com/rs/zerolog"
)

type Metrics struct {
	logger         zerolog.Logger
	hashrate       prometheus.Gauge
	connectedNodes prometheus.Gauge
	memoryUsage    prometheus.Gauge
}

func NewMetrics(logger zerolog.Logger) *Metrics {
	m := &Metrics{
		logger: logger,
		hashrate: prometheus.NewGauge(prometheus.GaugeOpts{
			Name: "pieracoin_hashrate",
			Help: "Current hashrate of the network",
		}),
		connectedNodes: prometheus.NewGauge(prometheus.GaugeOpts{
			Name: "pieracoin_connected_nodes",
			Help: "Number of connected nodes",
		}),
		memoryUsage: prometheus.NewGauge(prometheus.GaugeOpts{
			Name: "pieracoin_memory_usage",
			Help: "Memory usage in bytes",
		}),
	}
	prometheus.MustRegister(m.hashrate, m.connectedNodes, m.memoryUsage)
	return m
}

func (m *Metrics) Handler() http.Handler {
	return promhttp.Handler()
}

func (m *Metrics) UpdateHashrate(value float64) {
	m.hashrate.Set(value)
}

func (m *Metrics) UpdateConnectedNodes(count float64) {
	m.connectedNodes.Set(count)
}

func (m *Metrics) UpdateMemoryUsage(bytes float64) {
	m.memoryUsage.Set(bytes)
}