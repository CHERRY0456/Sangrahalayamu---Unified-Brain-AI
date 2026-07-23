'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { ArrowDown, Network, HelpCircle, RefreshCw } from 'lucide-react';

export interface ExplanationGraphNode {
  id: string;
  label: string;
  type: 'equipment' | 'action' | 'process' | 'compliance' | 'role';
  // Metadata for node click expansions
  description?: string;
  attributes?: Record<string, string>;
}

export interface ExplanationGraphLink {
  source: string;
  target: string;
  label?: string;
}

export interface ExplanationGraph {
  nodes: ExplanationGraphNode[];
  links: ExplanationGraphLink[];
}

interface GraphPreviewProps {
  graph: ExplanationGraph;
  interactive?: boolean;
}

export default function GraphPreview({
  graph,
  interactive = false,
}: GraphPreviewProps) {
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);

  const getNodeColor = (type: ExplanationGraphNode['type'], isSelected: boolean) => {
    if (isSelected) {
      return 'border-primary bg-primary/15 text-primary shadow-[0_0_15px_rgba(255,255,255,0.15)] scale-[1.03]';
    }
    switch (type) {
      case 'equipment':
        return 'bg-blue-500/10 border-blue-500/30 text-blue-500 hover:bg-blue-500/15';
      case 'action':
        return 'bg-amber-500/10 border-amber-500/30 text-amber-500 hover:bg-amber-500/15';
      case 'process':
        return 'bg-indigo-500/10 border-indigo-500/30 text-indigo-500 hover:bg-indigo-500/15';
      case 'compliance':
        return 'bg-emerald-500/10 border-emerald-500/30 text-emerald-500 hover:bg-emerald-500/15';
      case 'role':
        return 'bg-purple-500/10 border-purple-500/30 text-purple-500 hover:bg-purple-500/15';
    }
  };

  const handleNodeClick = (nodeId: string) => {
    if (!interactive) return;
    setSelectedNodeId((prev) => (prev === nodeId ? null : nodeId));
  };

  const handleReset = () => {
    setSelectedNodeId(null);
  };

  // Fetch expanded neighbor nodes from graph API when a node is selected
  const [expandedNodes, setExpandedNodes] = useState<{ id: string; label: string; type: ExplanationGraphNode['type'] }[]>([]);

  const fetchExpandedNodes = useCallback(async (nodeId: string) => {
    try {
      const res = await fetch(`/api/graph/neighbors/${nodeId}?depth=1`);
      if (res.ok) {
        const data = await res.json();
        // Map API response nodes to our format
        const neighbors = (data.nodes || []).map((n: { id: string; label?: string; type?: string }) => ({
          id: n.id,
          label: n.label || n.id,
          type: (n.type as ExplanationGraphNode['type']) || 'equipment',
        }));
        setExpandedNodes(neighbors);
      } else {
        setExpandedNodes([]);
      }
    } catch {
      setExpandedNodes([]);
    }
  }, []);

  useEffect(() => {
    if (selectedNodeId && interactive) {
      fetchExpandedNodes(selectedNodeId);
    } else {
      setExpandedNodes([]);
    }
  }, [selectedNodeId, interactive, fetchExpandedNodes]);
  const selectedNode = graph.nodes.find((n) => n.id === selectedNodeId);

  return (
    <div className="space-y-4 animate-in fade-in duration-150">
      <div className="flex justify-between items-center">
        <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider flex items-center gap-1.5">
          <Network className="h-3.5 w-3.5 text-primary shrink-0" />
          Knowledge Graph Schema
        </span>
        {interactive && selectedNodeId && (
          <button
            type="button"
            onClick={handleReset}
            className="inline-flex items-center gap-1 text-[9px] font-bold text-primary hover:underline cursor-pointer"
          >
            <RefreshCw className="h-3 w-3" />
            Reset Graph
          </button>
        )}
      </div>

      <div className="grid gap-4 lg:grid-cols-3 items-start">
        {/* Graph Render Box */}
        <div className="lg:col-span-2 rounded-lg border border-border bg-secondary/15 p-4 flex flex-col items-center space-y-2 min-h-64 justify-center relative">
          {graph.nodes.map((node, idx) => {
            const isSelected = selectedNodeId === node.id;
            const link = graph.links.find((l) => l.source === node.id);

            return (
              <React.Fragment key={node.id}>
                {/* Node Card */}
                <div
                  onClick={() => handleNodeClick(node.id)}
                  className={`rounded-lg border px-3.5 py-2 text-center text-xs font-bold shadow-sm transition-all min-w-[160px] select-none ${
                    interactive ? 'cursor-pointer' : ''
                  } ${getNodeColor(node.type, isSelected)}`}
                >
                  {node.label}
                </div>

                {/* Connecting Link Arrow */}
                {link && idx < graph.nodes.length - 1 && (
                  <div className="flex flex-col items-center py-1 text-muted-foreground">
                    <ArrowDown className="h-3.5 w-3.5" />
                    {link.label && (
                      <span className="text-[8px] text-muted-foreground/60 font-semibold uppercase tracking-wider mt-0.5">
                        {link.label}
                      </span>
                    )}
                  </div>
                )}
              </React.Fragment>
            );
          })}

          {/* Draw Expanded Neighbor Nodes if selected */}
          {interactive && expandedNodes.length > 0 && (
            <div className="pt-3 border-t border-border/40 w-full mt-4 space-y-2 flex flex-col items-center">
              <span className="text-[8px] text-muted-foreground/50 font-bold uppercase tracking-wider">
                Expanded Connected Entities
              </span>
              <div className="flex flex-wrap gap-2 justify-center">
                {expandedNodes.map((sub) => (
                  <div
                    key={sub.id}
                    className={`rounded-lg border px-2.5 py-1.5 text-center text-[10px] font-bold shadow-sm ${getNodeColor(
                      sub.type,
                      false
                    )}`}
                  >
                    {sub.label}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Node Attribute Inspector (Dashboard Interactive Only) */}
        {interactive && (
          <div className="rounded-lg border border-border bg-card p-4 space-y-3.5 min-h-[16rem]">
            <span className="text-[9px] font-bold text-muted-foreground uppercase tracking-wider block">
              Node Inspector
            </span>

            {selectedNode ? (
              <div className="space-y-3 text-xs animate-in fade-in duration-200">
                <div>
                  <h4 className="font-bold text-foreground">{selectedNode.label}</h4>
                  <span className="inline-block rounded bg-secondary px-1.5 py-0.5 text-[8px] font-extrabold uppercase text-muted-foreground border border-border mt-1">
                    Class: {selectedNode.type}
                  </span>
                </div>
                <div>
                  <span className="font-bold text-[9px] uppercase tracking-wide text-muted-foreground block mb-0.5">
                    Description
                  </span>
                  <p className="text-muted-foreground leading-relaxed">
                    {selectedNode.description || 'Enterprise database entity matching safety guidelines or maintenance log checklists.'}
                  </p>
                </div>
                {selectedNode.attributes && (
                  <div>
                    <span className="font-bold text-[9px] uppercase tracking-wide text-muted-foreground block mb-1">
                      Properties
                    </span>
                    <div className="space-y-1 rounded border border-border/60 p-2 bg-secondary/10">
                      {Object.entries(selectedNode.attributes).map(([key, val]) => (
                        <div key={key} className="flex justify-between text-[10px]">
                          <span className="text-muted-foreground capitalize">{key}:</span>
                          <span className="text-foreground font-bold">{val}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center text-center text-muted-foreground italic h-48 space-y-2">
                <HelpCircle className="h-6 w-6 text-muted-foreground/60" />
                <div className="text-[10px] max-w-[140px] leading-normal">
                  Click any graph node to inspect properties and expand relations.
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
