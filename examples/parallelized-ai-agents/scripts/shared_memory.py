#!/usr/bin/env python3
"""
Shared memory implementation for parallel AI agents.
Provides thread-safe storage for agent discoveries, patterns, and coordination.
"""

import json
import fcntl
import os
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import hashlib


@dataclass
class AgentDiscovery:
    """Represents a discovery or learning from an agent"""
    agent_id: str
    key: str
    value: Any
    timestamp: str
    confidence: float = 1.0
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class AgentMemory:
    """Thread-safe shared memory for parallel AI agents"""
    
    def __init__(self, memory_path: str = "/shared/agent_memory.json"):
        self.memory_path = Path(memory_path)
        self.memory_path.parent.mkdir(parents=True, exist_ok=True)
        self.lock_path = self.memory_path.with_suffix('.lock')
        self._initialize_memory()
    
    def _initialize_memory(self):
        """Initialize memory file if it doesn't exist"""
        if not self.memory_path.exists():
            with open(self.memory_path, 'w') as f:
                json.dump({
                    "discoveries": {},
                    "conflicts": [],
                    "decisions": {},
                    "metadata": {
                        "created": datetime.utcnow().isoformat(),
                        "version": "1.0"
                    }
                }, f, indent=2)
    
    def _acquire_lock(self, exclusive: bool = True):
        """Acquire file lock for thread-safe operations"""
        lock_file = open(self.lock_path, 'w')
        lock_type = fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH
        fcntl.flock(lock_file, lock_type)
        return lock_file
    
    def _release_lock(self, lock_file):
        """Release file lock"""
        fcntl.flock(lock_file, fcntl.LOCK_UN)
        lock_file.close()
    
    def record_discovery(self, discovery: AgentDiscovery):
        """Record a new discovery from an agent"""
        lock_file = self._acquire_lock()
        try:
            with open(self.memory_path, 'r') as f:
                memory = json.load(f)
            
            agent_discoveries = memory["discoveries"].setdefault(discovery.agent_id, {})
            
            # Check for conflicts with other agents
            conflict_found = False
            for other_agent, discoveries in memory["discoveries"].items():
                if other_agent != discovery.agent_id and discovery.key in discoveries:
                    # Record potential conflict
                    conflict = {
                        "key": discovery.key,
                        "agents": [discovery.agent_id, other_agent],
                        "values": [discovery.value, discoveries[discovery.key]["value"]],
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    memory["conflicts"].append(conflict)
                    conflict_found = True
            
            # Store discovery
            agent_discoveries[discovery.key] = asdict(discovery)
            
            # Update metadata
            memory["metadata"]["last_updated"] = datetime.utcnow().isoformat()
            memory["metadata"]["total_discoveries"] = sum(
                len(discoveries) for discoveries in memory["discoveries"].values()
            )
            
            with open(self.memory_path, 'w') as f:
                json.dump(memory, f, indent=2)
            
            return not conflict_found
            
        finally:
            self._release_lock(lock_file)
    
    def get_shared_knowledge(self, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """Retrieve shared knowledge, optionally filtered by agent"""
        lock_file = self._acquire_lock(exclusive=False)
        try:
            with open(self.memory_path, 'r') as f:
                memory = json.load(f)
            
            if agent_id:
                return memory["discoveries"].get(agent_id, {})
            return memory
            
        finally:
            self._release_lock(lock_file)
    
    def get_conflicts(self) -> List[Dict[str, Any]]:
        """Get all recorded conflicts between agents"""
        lock_file = self._acquire_lock(exclusive=False)
        try:
            with open(self.memory_path, 'r') as f:
                memory = json.load(f)
            return memory.get("conflicts", [])
            
        finally:
            self._release_lock(lock_file)
    
    def record_decision(self, key: str, decision: Dict[str, Any], decided_by: str):
        """Record a decision made to resolve conflicts or choose implementations"""
        lock_file = self._acquire_lock()
        try:
            with open(self.memory_path, 'r') as f:
                memory = json.load(f)
            
            memory["decisions"][key] = {
                "decision": decision,
                "decided_by": decided_by,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            with open(self.memory_path, 'w') as f:
                json.dump(memory, f, indent=2)
                
        finally:
            self._release_lock(lock_file)
    
    def get_agent_summary(self) -> Dict[str, Any]:
        """Get summary statistics about agent activities"""
        lock_file = self._acquire_lock(exclusive=False)
        try:
            with open(self.memory_path, 'r') as f:
                memory = json.load(f)
            
            summary = {
                "total_agents": len(memory["discoveries"]),
                "total_discoveries": memory["metadata"].get("total_discoveries", 0),
                "total_conflicts": len(memory.get("conflicts", [])),
                "total_decisions": len(memory.get("decisions", {})),
                "agents": {}
            }
            
            for agent_id, discoveries in memory["discoveries"].items():
                summary["agents"][agent_id] = {
                    "discovery_count": len(discoveries),
                    "last_activity": max(
                        (d["timestamp"] for d in discoveries.values()),
                        default="Never"
                    )
                }
            
            return summary
            
        finally:
            self._release_lock(lock_file)
    
    def checkpoint(self, checkpoint_name: str):
        """Create a checkpoint of current memory state"""
        lock_file = self._acquire_lock(exclusive=False)
        try:
            checkpoint_path = self.memory_path.parent / f"checkpoint_{checkpoint_name}_{int(time.time())}.json"
            with open(self.memory_path, 'r') as f:
                memory = json.load(f)
            
            memory["metadata"]["checkpoint_name"] = checkpoint_name
            memory["metadata"]["checkpoint_time"] = datetime.utcnow().isoformat()
            
            with open(checkpoint_path, 'w') as f:
                json.dump(memory, f, indent=2)
            
            return str(checkpoint_path)
            
        finally:
            self._release_lock(lock_file)


# Example usage functions
def example_agent_workflow(agent_id: str, memory: AgentMemory):
    """Example of how an agent would use shared memory"""
    
    # Record a discovery
    discovery = AgentDiscovery(
        agent_id=agent_id,
        key="api_endpoint_pattern",
        value={
            "pattern": "/api/v1/{resource}/{id}",
            "methods": ["GET", "POST", "PUT", "DELETE"]
        },
        timestamp=datetime.utcnow().isoformat(),
        confidence=0.95,
        tags=["api", "rest", "pattern"]
    )
    
    success = memory.record_discovery(discovery)
    if not success:
        print(f"[{agent_id}] Potential conflict detected for key: {discovery.key}")
    
    # Check for relevant knowledge from other agents
    all_knowledge = memory.get_shared_knowledge()
    for other_agent, discoveries in all_knowledge["discoveries"].items():
        if other_agent != agent_id:
            for key, value in discoveries.items():
                if "api" in value.get("tags", []):
                    print(f"[{agent_id}] Found relevant API pattern from {other_agent}: {key}")


if __name__ == "__main__":
    # Demo the shared memory system
    memory = AgentMemory("./demo_memory.json")
    
    # Simulate multiple agents
    example_agent_workflow("frontend_agent", memory)
    example_agent_workflow("backend_agent", memory)
    
    # Show summary
    summary = memory.get_agent_summary()
    print("\nAgent Activity Summary:")
    print(json.dumps(summary, indent=2))
    
    # Show conflicts if any
    conflicts = memory.get_conflicts()
    if conflicts:
        print("\nDetected Conflicts:")
        print(json.dumps(conflicts, indent=2))