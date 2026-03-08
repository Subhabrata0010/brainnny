from typing import List, Dict, Any, Optional
from app.models.schemas import PageResponse, NodeResponse


class PromptAssembler:
    """Service for assembling contextualized prompts."""
    
    @staticmethod
    def assemble_prompt(
        query: str,
        pages: List[PageResponse],
        nodes: List[NodeResponse],
        user_profile: Optional[Dict[str, Any]] = None,
        commitments: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        Assemble final prompt with all context.
        
        Format:
        [User Profile]
        [Relevant Page Summaries]
        [Relevant Nodes]
        [Open Commitments]
        [Current User Query]
        
        Args:
            query: User's current query
            pages: Relevant pages from memory
            nodes: Relevant nodes from memory
            user_profile: User profile data
            commitments: Open commitments
        
        Returns:
            Assembled prompt string
        """
        sections = []
        
        if user_profile:
            profile_text = "=== USER PROFILE ===\n"
            if user_profile.get("communication_style"):
                profile_text += f"Communication Style: {user_profile['communication_style']}\n"
            if user_profile.get("recurring_topics"):
                topics = ", ".join(user_profile["recurring_topics"])
                profile_text += f"Recurring Topics: {topics}\n"
            sections.append(profile_text)
        
        if pages:
            pages_text = "=== RELEVANT CONVERSATION SUMMARIES ===\n"
            for i, page in enumerate(pages, 1):
                pages_text += f"\n{i}. {page.session_title}\n"
                pages_text += f"   {page.summary}\n"
                pages_text += f"   (Importance: {page.importance_score:.2f})\n"
            sections.append(pages_text)
        
        if nodes:
            nodes_text = "=== RELEVANT MEMORY DETAILS ===\n"
            
            nodes_by_type = {}
            for node in nodes:
                if node.node_type not in nodes_by_type:
                    nodes_by_type[node.node_type] = []
                nodes_by_type[node.node_type].append(node)
            
            for node_type, type_nodes in nodes_by_type.items():
                nodes_text += f"\n{node_type.upper()}S:\n"
                for node in type_nodes:
                    nodes_text += f"  • {node.content}\n"
            
            sections.append(nodes_text)
        
        if commitments:
            commit_text = "=== OPEN COMMITMENTS ===\n"
            for i, commit in enumerate(commitments, 1):
                commit_text += f"{i}. {commit['content']}\n"
                if commit.get('reminder_date'):
                    commit_text += f"   Due: {commit['reminder_date']}\n"
            sections.append(commit_text)
        
        query_text = f"=== CURRENT QUERY ===\n{query}"
        sections.append(query_text)
        
        return "\n\n".join(sections)