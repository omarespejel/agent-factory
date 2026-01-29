/// Key Image Tracker Module
/// 
/// Prevents double-spending by tracking unique key images.
/// Each Monero transaction output can only be spent once.
///
/// # Security
/// - Append-only storage (no deletions)
/// - Protected by Ownable access control

use core::integer::u256;

/// Interface for key image tracking
#[starknet::interface]
pub trait IKeyImageTracker<TContractState> {
    /// Records a key image as used
    /// 
    /// # Arguments
    /// * `key_image` - The key image to record
    ///
    /// # Returns
    /// * `bool` - True if successfully recorded (was not already used)
    fn record_key_image(ref self: TContractState, key_image: felt252) -> bool;

    /// Checks if a key image has been used
    fn is_used(self: @TContractState, key_image: felt252) -> bool;

    /// Returns the total count of recorded key images
    fn get_count(self: @TContractState) -> u256;
}

/// TODO: Agent will implement key image tracking with OZ Ownable
